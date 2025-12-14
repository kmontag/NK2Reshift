SYSTEM_MIDI_REMOTE_SCRIPTS_DIR := /Applications/Ableton\ Live\ 12\ Suite.app/Contents/App-Resources/MIDI\ Remote\ Scripts

.PHONY: deps
deps: __ext__/System_MIDIRemoteScripts/.make.decompile .make.poetry-install

.PHONY: check
check: .make.poetry-install __ext__/System_MIDIRemoteScripts/.make.decompile
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
	rm -rf __ext/System_MIDIRemoteScripts/
	rm -f .make.*

__ext__/System_MIDIRemoteScripts/.make.decompile: $(SYSTEM_MIDI_REMOTE_SCRIPTS_DIR) | .make.poetry-install
	rm -rf $(@D)/
	mkdir -p $(@D)/ableton/
# decompyle3 works for most files, and the ones where it throws errors
# don't matter for our purposes.
	poetry run decompyle3 -r -o $(@D)/ableton/ $(SYSTEM_MIDI_REMOTE_SCRIPTS_DIR)/ableton/
	touch "$@"

.make.poetry-install: pyproject.toml poetry.lock
	poetry install
	touch "$@"
