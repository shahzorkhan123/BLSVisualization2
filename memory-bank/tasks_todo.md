# Tasks TODO

## Phase 5: Data Pipeline (Current)
- [x] Create memory-bank/ directory
- [ ] Create scripts/pipeline/__init__.py, config.py
- [ ] Create scripts/pipeline/db.py
- [ ] Create scripts/pipeline/import_csv.py
- [ ] Create scripts/pipeline/export_csv.py
- [ ] Create scripts/pipeline/export_jsonp.py
- [ ] Create scripts/pipeline/validate.py
- [ ] Create scripts/pipeline/run_pipeline.py
- [ ] Run pipeline (--year 2024 --fresh)
- [ ] Verify output (~720 records, treemaps render)
- [ ] Fix tests (Region_Type, remove xfail)
- [ ] Create tests/test_pipeline.py
- [ ] Create docs/adding_country.md
- [ ] Update CLAUDE.md and .gitignore

## Future
- Phase 6: CI/CD (optional)
- Real complexity framework (O*NET task data)
- Multi-country frontend support
- String pooling optimization (if data grows large)
