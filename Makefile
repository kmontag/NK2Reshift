# Auto-detect system MIDI Remote Scripts directory, or allow override.
# Set to empty to skip decompilation: make SYSTEM_MIDI_REMOTE_SCRIPTS_DIR=
ifeq ($(origin SYSTEM_MIDI_REMOTE_SCRIPTS_DIR),undefined)
  ifeq ($(shell uname -s),Darwin)
    # macOS: Find any Live 12 installation (Suite, Standard, or Intro).
    SYSTEM_MIDI_REMOTE_SCRIPTS_DIR := $(shell find /Applications -maxdepth 1 -name "Ableton Live 12*.app" -print -quit 2>/dev/null | sed 's|$$|/Contents/App-Resources/MIDI Remote Scripts|')
  else ifeq ($(OS),Windows_NT)
    # Windows: Query registry for Ableton installation path.
    ABLETON_PATH := $(shell powershell -Command "(Get-ItemProperty 'HKLM:\\SOFTWARE\\Ableton\\Live 12' -Name InstallLocation -ErrorAction SilentlyContinue).InstallLocation" 2>/dev/null)
    ifneq ($(ABLETON_PATH),)
      SYSTEM_MIDI_REMOTE_SCRIPTS_DIR := $(ABLETON_PATH)/Resources/MIDI Remote Scripts
    endif
  endif
endif


# Find all .pyc files in ableton/ and generate corresponding .py
# target paths. Use shell to handle the path transformation to avoid
# Make's space-splitting issues. Exclude default_bank_definitions.py -
# pylingual doesn't seem to be able to handle it yet.
# If SYSTEM_MIDI_REMOTE_SCRIPTS_DIR is empty, this evaluates to empty list.
ABLETON_PY_FILES := $(shell \
	if [ -n "$(SYSTEM_MIDI_REMOTE_SCRIPTS_DIR)" ] && [ -d "$(SYSTEM_MIDI_REMOTE_SCRIPTS_DIR)" ]; then \
		find "$(SYSTEM_MIDI_REMOTE_SCRIPTS_DIR)/ableton" -name "*.pyc" -type f 2>/dev/null | \
		grep -v 'default_bank_definitions\.pyc' | \
		sed 's|$(SYSTEM_MIDI_REMOTE_SCRIPTS_DIR)/\(.*\)\.pyc|__ext__/System_MIDIRemoteScripts/\1.py|'; \
	fi)


.PHONY: deps
deps: $(ABLETON_PY_FILES) .make.poetry-install
ifeq ($(ABLETON_PY_FILES),)
	@echo "Note: Skipping Ableton library decompilation."
	@echo "SYSTEM_MIDI_REMOTE_SCRIPTS_DIR is not set or directory not found."
	@echo "Type checking will work without full Ableton API definitions."
endif

.PHONY: check
check: .make.poetry-install $(ABLETON_PY_FILES)
	poetry run pyright .

.PHONY: lint
lint: .make.poetry-install
	poetry run ruff format --check .
	poetry run ruff check .

.PHONY: fix
fix: .make.poetry-install
	poetry run ruff format .
	poetry run ruff check --fix .

.PHONY: clean
clean:
	rm -rf .venv/
	rm -rf __ext__/System_MIDIRemoteScripts/
	rm -rf __ext__/pylingual/venv/
	rm -rf __ext__/pyenv/versions/
	rm -f .make.*

# Initialize and update pyenv submodule, install Python 3.11.
.make.pyenv-install: .gitmodules
	@pwd_check=$$(pwd) && \
	if echo "$$pwd_check" | grep -q ' '; then \
		echo "ERROR: Physical directory path contains spaces: $$pwd_check"; \
		echo "pyenv cannot build Python in directories with spaces."; \
		echo ""; \
		echo "Suggested workaround:"; \
		echo "  1. Create a symlink without spaces:"; \
		echo "     ln -s '$$pwd_check' ~/nk2reshift"; \
		echo "  2. Run make from the symlink:"; \
		echo "     cd ~/nk2reshift && make"; \
		exit 1; \
	fi
	git submodule update --init __ext__/pyenv
	export PYENV_ROOT="$$(pwd)/__ext__/pyenv" && \
		export PATH="$$PYENV_ROOT/bin:$$PATH" && \
		pyenv install -s 3.11
	touch "$@"

# Initialize and update the pylingual submodule, then set up its venv.
__ext__/pylingual/venv/bin/pylingual: .gitmodules
	git submodule update --init __ext__/pylingual
# The poetry version might not be exactly in sync with pylingual's
# lockfile, so we need to run `poetry lock` before installing.
# However, this modifies the lockfile, so we also reset it after the
# install to avoid messy git diffs.
	cd __ext__/pylingual && \
		python -m venv venv && \
		. venv/bin/activate && \
		pip install "poetry>=2.0" && \
		poetry lock && \
		poetry install && \
		git checkout poetry.lock
	touch "$@"

# Pattern rule: decompile individual .pyc file to .py file. The
# dependency on pylingual is defined as order-only, since these builds
# take a lot of resources and we don't want to re-run e.g. every time
# pyproject is touched. The `clean` target can be used to force
# regeneration.
# Only defined if SYSTEM_MIDI_REMOTE_SCRIPTS_DIR is set.
ifneq ($(SYSTEM_MIDI_REMOTE_SCRIPTS_DIR),)
__ext__/System_MIDIRemoteScripts/%.py: | __ext__/pylingual/venv/bin/pylingual .make.pyenv-install
	@mkdir -p $(@D)
	@echo "Decompiling: $*.pyc"
# Since we're somewhat likely to be in a directory with spaces
# somewhere in the path (e.g. "Remote Scripts"), the plyingual binary
# from the venv might have a shebang with spaces, which doesn't work
# very well. We instead run pylingual directly through the python
# binary.
	@PYENV_ROOT="$$(pwd)/__ext__/pyenv" \
		PATH="$$PYENV_ROOT/bin:$$PATH" \
		./__ext__/pylingual/venv/bin/python ./__ext__/pylingual/venv/bin/pylingual \
			-q \
			-o $(@D) \
			"$(SYSTEM_MIDI_REMOTE_SCRIPTS_DIR)/$*.pyc"
	@mv "$(@D)/decompiled_$(@F)" "$@"
	@echo "Finished decompiling: $*.pyc"
endif

.make.poetry-install: pyproject.toml poetry.lock
	poetry install
	touch "$@"
