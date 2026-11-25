PY ?= .venv/bin/python
.PHONY: film setup validate keyframes shots music narration assemble clean smoke
film: validate keyframes shots music narration assemble
	@echo "Done: see outputs/final/"
setup:
	python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt
	@command -v ffmpeg >/dev/null || echo "Install ffmpeg: brew install ffmpeg"
validate:
	$(PY) -m pipeline.validate
keyframes: ; $(PY) -m pipeline.keyframes
shots: ; $(PY) -m pipeline.shots
music: ; $(PY) -m pipeline.music
narration: ; $(PY) -m pipeline.narration
assemble: ; $(PY) -m pipeline.assemble
smoke: ; $(PY) -m pipeline.smoke
clean: ; rm -rf outputs/* .cache
