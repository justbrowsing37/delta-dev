"""Seed and content-loading scripts.

Run individual seeders as modules, e.g.:
    python -m seeds.load_content        # sync markdown curriculum into the DB
    python -m seeds.curriculum_seed     # legacy hardcoded curriculum seed

Intentionally left import-free so that importing the ``seeds`` package has no
side effects (the individual scripts build their own app when run).
"""
