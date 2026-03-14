SKILL_ID := core
VERSION := 1.0.0

OUTPUT_DIR := executors

.PHONY: all
all: build

.PHONY: build
build: build-darwin build-linux

.PHONY: build-darwin
build-darwin:
	@echo "Building core skill plugin for darwin-arm64..."
	@mkdir -p $(OUTPUT_DIR)
	CGO_ENABLED=1 GOOS=darwin GOARCH=arm64 go build \
		-buildmode=plugin \
		-o $(OUTPUT_DIR)/$(SKILL_ID)-darwin-arm64.so \
		./executors/*.go
	@echo "Plugin built: $(OUTPUT_DIR)/$(SKILL_ID)-darwin-arm64.so"

.PHONY: build-linux
build-linux:
	@echo "Building core skill plugin for linux-amd64..."
	@mkdir -p $(OUTPUT_DIR)
	CGO_ENABLED=1 GOOS=linux GOARCH=amd64 go build \
		-buildmode=plugin \
		-o $(OUTPUT_DIR)/$(SKILL_ID)-linux-amd64.so \
		./executors/*.go
	@echo "Plugin built: $(OUTPUT_DIR)/$(SKILL_ID)-linux-amd64.so"

.PHONY: test
test:
	go test -v ./executors/...

.PHONY: clean
clean:
	rm -f $(OUTPUT_DIR)/*.so

.PHONY: deps
deps:
	go mod download
	go mod tidy
