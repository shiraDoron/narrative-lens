import os
import torch
import torch.nn as nn
import pandas as pd
from bertopic import BERTopic
from narrative_lens.config import NUM_TOPICS, NUM_NARRATIVES, TOPIC_MODEL_PATH_LEGACY
# Shared (train + inference) preprocessing - see topic_preprocessing.py docstring. MUST be the
# exact same function train_topics.py applies before BERTopic.fit(), applied here ONLY when
# model_path != TOPIC_MODEL_PATH_LEGACY (see TopicAnalysisPipeline.__init__ below).
from narrative_lens.topic_modeling.topic_preprocessing import clean_text_for_topic_model, build_multiword_label

# שכבת הלמידה מהנושאים (ללא ממד העמדות)
class TopicStanceLayer(nn.Module):
    def __init__(self):
        super(TopicStanceLayer, self).__init__()

        self.num_topics = NUM_TOPICS
        self.num_narratives = NUM_NARRATIVES

        # גודל המילון מבוסס כעת על מספר הנושאים בלבד
        self.matrix_size = self.num_topics
        self.weights = nn.Embedding(self.matrix_size, self.num_narratives)

        # אתחול המשקולות באופן אחיד
        nn.init.uniform_(self.weights.weight, 0, 1)

    # פונקציית הלמידה - מקבלת נושאים בלבד
    def forward(self, topic_ids):
        # הגדרת אינדקס ה-OOV כנושא האחרון (499)
        oov_topic_index = self.num_topics - 1

        # הגנה: החלפת -1 או חריגות (מעל 499) באינדקס ה-OOV
        safe_topic_ids = torch.where(
            (topic_ids == -1) | (topic_ids >= self.num_topics),
            torch.tensor(oov_topic_index, device=topic_ids.device),
            topic_ids
        )

        # ויดוא סופי שהאינדקס לא חורג מטווח המטריצה
        indices = torch.clamp(safe_topic_ids, 0, self.matrix_size - 1)

        # שליפת הוקטורים המתאימים ישירות לפי אינדקס הנושא
        narrative_vectors = self.weights(indices)

        return narrative_vectors

# הרצת המודל לזיהוי נושאים בלבד
class TopicAnalysisPipeline:
    # model_path ברירת המחדל הוא המודל ה"ישן"/הקפוא (TOPIC_MODEL_PATH_LEGACY, ראו config.py) -
    # זה שעליו אומנו הצ'קפוינטים הקיימים (best_narrative_model_hybrid.pth,
    # best_model_hybrid_architecture.pth) דרך TopicStanceLayer. אין לשנות ברירת מחדל זו -
    # fusion.py קורא ל-TopicAnalysisPipeline() ללא פרמטרים ומצפה למודל הזה בדיוק.
    # כדי להשתמש במודל החדש התומך ב-soft clustering (approximate_distribution), יש להעביר
    # מפורשות model_path=config.TOPIC_MODEL_PATH_SOFT (למשל, כפי שעושה analyze_soft_topics.py).
    def __init__(self, model_path=TOPIC_MODEL_PATH_LEGACY):
        print(f"Loading pre-trained Topic Model from '{model_path}'...")
        self.model_path = model_path
        # מחיל את אותו ניקוי (clean_text_for_topic_model, ראו topic_preprocessing.py) ששימש
        # באימון - אבל ורק כאשר לא מדובר במודל הישן/הקפוא. המודל הישן (TOPIC_MODEL_PATH_LEGACY)
        # אומן ללא הניקוי הזה, והצ'קפוינטים הקיימים (best_narrative_model_hybrid.pth,
        # best_model_hybrid_architecture.pth) תלויים בהתנהגות המקורית (ללא ניקוי) שלו - אסור
        # לשנות זאת. כל model_path אחר (בפועל היום: TOPIC_MODEL_PATH_SOFT) מקבל את הניקוי,
        # כדי להתאים בדיוק למה ש-train_topics.py הריץ לפני ה-fit.
        self.use_cleaned_preprocessing = (model_path != TOPIC_MODEL_PATH_LEGACY)
        # טעינת המודל המוכן מהתיקייה שהתקבלה (ברירת מחדל: התיקייה הישנה/הקפואה)
        self.topic_model = BERTopic.load(model_path)
        # תוויות שכוללו ע"י LLM (llm_topic_refiner.py), אם קיימות - אופציונלי,
        # לא משפיע על הסיווג עצמו, רק על פרשנות אנושית של הנושא.
        try:
            from narrative_lens.topic_modeling.llm_topic_refiner import load_refined_labels
            self.llm_labels = load_refined_labels(os.path.join(model_path, "topics_llm_refined.json"))
        except Exception:
            self.llm_labels = {}
        print("Pipeline is ready!")

    def _prepare_text(self, text):
        """מחיל את ניקוי ה-preprocessing המשותף (URLs/@mentions/#hashtags) אם ורק אם המודל
        הטעון הוא לא המודל הישן/הקפוא - ראו הערה ב-__init__."""
        if self.use_cleaned_preprocessing:
            return clean_text_for_topic_model(text)
        return text

    def get_topic_label(self, topic_id, top_n_words=1):
        """מחזיר תווית קריאה לנרטיב: תווית LLM אם קיימת, אחרת top_n_words המילים
        המובילות של ייצוג ה-topic ב-BERTopic (c-TF-IDF, או ייצוג אחר אם הוגדר
        representation_model), מחוברות ברווח.

        ברירת המחדל top_n_words=1 שומרת על ההתנהגות המקורית (מילה בודדת) בדיוק -
        חשוב לתאימות לאחור: fusion.py/train.py והמודל הישן/הקפוא (TOPIC_MODEL_PATH_LEGACY)
        וה-checkpoints הקיימים (best_narrative_model_hybrid.pth וכו') אינם משתמשים
        ב-label הזה לסיווג בפועל (הוא רק לתצוגה/פרשנות אנושית), אבל אין סיבה לשנות את
        ברירת המחדל בכל זאת - כדי לא ליצור אי-עקביות בין קריאות שונות. קוראים שרוצים
        label רב-מילי וקריא יותר (למשל עבור saved_topic_model_soft_v2) יכולים להעביר
        top_n_words=3 (או כל מספר אחר) במפורש.
        """
        if topic_id == -1:
            return "לא זוהה"
        refined = self.llm_labels.get(topic_id)
        if refined and refined.get("label"):
            return refined["label"]
        info = self.topic_model.get_topic(topic_id)
        if not info:
            return "לא זוהה"
        if top_n_words <= 1:
            return info[0][0]
        label = build_multiword_label(info, top_n_words=top_n_words)
        return label if label else "לא זוהה"

    # מזהה נושא מרכזי בלבד ומחזירה אותו
    # לא לשנות! ממשק זה משמש את fusion.py/train.py (topic_id בודד, hard assignment) -
    # התאימות לאחור נשמרת במכוון - ראו get_topic_distribution/process_text_with_distribution
    # למטה עבור חלוקת נושאים "רכה" (multi-topic), שהיא תוספת נפרדת ואינה נוגעת בזרימה הזו.
    def process_text(self, text):
        text = self._prepare_text(text)
        topics, probs = self.topic_model.transform([text])
        main_topic_id = topics[0]

        # החזרת מזהה הנושא בלבד (ללא ערך עמדה)
        if main_topic_id == -1:
            return -1

        return main_topic_id

    def get_topic_distribution(self, text, top_n=3):
        """
        חלוקת נושאים "רכה" (soft/multi-topic) לטקסט בודד, בנוסף (לא במקום) ל-topic_id
        הבודד/hard שמחזיר process_text.

        משתמש ב-approximate_distribution() של BERTopic - ציון דמיון token-level/c-TF-IDF
        של הטקסט מול כל נושא (לא posterior הסתברותי אמיתי של HDBSCAN, אבל הרבה יותר מהיר
        ולא דורש calculate_probabilities=True/refit של שלב ה-clustering עצמו - ראו הסבר
        מפורט בדיון עם המשתמש). דורש שהמודל השמור נטען עם vectorizer_model/c_tf_idf_
        מאותחלים - כלומר שנשמר עם save_ctfidf=True (train_topics.py) - אחרת נכשל עם
        NotFittedError. models/saved_topic_model (ברירת המחדל של TopicAnalysisPipeline)
        נשמר בלי save_ctfidf כדי לשמור על תאימות מלאה לצ'קפוינטים הקיימים - כדי לקבל
        חלוקה רכה אמיתית יש לטעון TopicAnalysisPipeline(model_path=config.TOPIC_MODEL_PATH_SOFT).

        מחזיר רשימה ממוינת יורד לפי score, עד top_n פריטים, כל אחד:
            {"topic_id": int, "score": float, "label": str}
        הציונים מנורמלים כך שסכומם הוא 1.0 (יחסית לנושאים שהוחזרו ב-top_n, לא לכל 369
        הנושאים) - approximate_distribution כשלעצמו לא מבטיח נרמול הדוק לנושאים הרלוונטיים.
        אם approximate_distribution נכשל (למשל מודל ישן ללא save_ctfidf=True) או שאין
        לטקסט אף נושא עם ציון חיובי, מוחזרת רשימה ריקה [].
        """
        text = self._prepare_text(text)
        try:
            topic_distr, _ = self.topic_model.approximate_distribution([text])
        except Exception as e:
            print(f"[!] approximate_distribution נכשל ({e}) - ייתכן שהמודל השמור לא "
                  f"נשמר עם save_ctfidf=True. מחזיר רשימה ריקה.")
            return []

        scores = topic_distr[0]
        nonzero_idx = [i for i, s in enumerate(scores) if s > 0]
        if not nonzero_idx:
            return []

        nonzero_idx.sort(key=lambda i: scores[i], reverse=True)
        top_idx = nonzero_idx[:top_n]

        total = sum(scores[i] for i in top_idx)
        if total <= 0:
            return []

        return [
            {
                "topic_id": int(i),
                "score": float(scores[i] / total),
                "label": self.get_topic_label(int(i)),
            }
            for i in top_idx
        ]

    def process_text_with_distribution(self, text, top_n=3):
        """
        נקודת כניסה חדשה, נפרדת מ-process_text (שנשאר ללא שינוי): מחזירה גם את
        ה-topic_id הקשיח/דומיננטי (זהה למה שprocess_text היה מחזיר) וגם את חלוקת
        הנושאים הרכה. לא בשימוש עדיין ע"י fusion.py/train.py - תוסף עצמאי.
        """
        return {
            "topic_id": self.process_text(text),
            "topic_distribution": self.get_topic_distribution(text, top_n=top_n),
        }


# --- קוד בדיקה (טסט) מעודכן ---
if __name__ == "__main__":
    print("מתחיל אתחול מודלים (זה עשוי לקחת כמה שניות)...")
    pipeline = TopicAnalysisPipeline()

    # טעינת מאגר נתוני הבדיקה
    with open("gemini_natural_dataset.csv", "r", encoding="utf-8") as f:
        test_full_data = [line.strip() for line in f if line.strip()]

    # משפטי בדיקה שנרצה לנתח
    test_sentences = test_full_data[:10]

    print("\n--- תוצאות הניתוח ---")
    for sentence in test_sentences:
        topic_id = pipeline.process_text(sentence)
        test_topic_name = pipeline.get_topic_label(topic_id)

        print(f"טקסט: '{sentence}'")
        print(f"נושא שזוהה: {test_topic_name} (ID: {topic_id})\n")