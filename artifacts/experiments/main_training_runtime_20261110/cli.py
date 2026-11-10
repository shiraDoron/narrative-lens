"""Explicit commands: prepare-human, train (gated), source-audit. Never evaluate test."""

import argparse
import json
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare = commands.add_parser('prepare-human')
    for field in ['train-labels', 'validation-labels', 'pair-reviews', 'signed-freeze']:
        prepare.add_argument('--' + field, type=Path, required=True)
    prepare.add_argument('--name', required=True)
    train = commands.add_parser('train')
    train.add_argument('--approved-snapshot', type=Path, required=True)
    train.add_argument('--run-name', required=True)
    train.add_argument('--cohort', choices=['primary_all_attempted', 'secondary_common_accepted'], default='primary_all_attempted')
    commands.add_parser('source-audit')
    args = parser.parse_args()
    try:
        if args.command == 'prepare-human':
            from data import approve
            print(approve(args.train_labels, args.validation_labels, args.pair_reviews, args.signed_freeze, args.name))
        elif args.command == 'source-audit':
            from data import source_audit
            print(json.dumps(source_audit(), indent=2))
        else:
            if not re.fullmatch(r'[A-Za-z0-9_-]+', args.run_name):
                raise ValueError('Use a new simple run name')
            from contract import HERE
            from trainer import run_scientific
            run_scientific(args.approved_snapshot, HERE / 'runs' / args.run_name, args.cohort)
    except (ValueError, FileNotFoundError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
