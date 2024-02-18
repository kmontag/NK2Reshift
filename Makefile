SYSTEM_MIDI_REMOTE_SCRIPTS_DIR := /Applications/Ableton\ Live\ 11\ Suite.app/Contents/App-Resources/MIDI\ Remote\ Scripts

.PHONY: deps
deps: __ext__/System_MIDIRemoteScripts/.make.decompile .make.pip-install

.PHONY: check
check: .make.pip-install __ext__/System_MIDIRemoteScripts/.make.decompile
	pyright .

.PHONY: lint
lint: .make.pip-install
	ruff format --check .
	ruff check .

.PHONY: fix
fix: .make.pip-install
	ruff format .
	ruff check --fix .

__ext__/System_MIDIRemoteScripts/.make.decompile: $(SYSTEM_MIDI_REMOTE_SCRIPTS_DIR) | .make.pip-install
	rm -rf $(@D)/
	mkdir -p $(@D)/ableton/
# decompyle3 works for most files, and the ones where it throws errors
# don't matter for our purposes.
	decompyle3 -r -o $(@D)/ableton/ $(SYSTEM_MIDI_REMOTE_SCRIPTS_DIR)/ableton/
	touch $@

.make.pip-install: requirements.txt .python-version
	pip install -r requirements.txt
	touch .make.pip-install
