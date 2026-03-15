package main

import (
	"context"

	"github.com/axiom-studio/skills.sdk/deps"
	"github.com/axiom-studio/skills.sdk/executor"
	"github.com/axiom-studio/skills.sdk/skill"
)

// CoreSkillPlugin implements the SkillPlugin interface from the SDK
type CoreSkillPlugin struct {
	logger     deps.Logger
	k8sClient  interface{}
	httpClient interface{}
}

func (p *CoreSkillPlugin) Initialize(config map[string]interface{}) error {
	// Extract dependencies from config using SDK keys
	if logger, ok := config[deps.LoggerKey].(deps.Logger); ok {
		p.logger = logger
	}

	if k8s, ok := config[deps.K8sClientKey]; ok {
		p.k8sClient = k8s
	}

	if http, ok := config[deps.HTTPClientKey]; ok {
		p.httpClient = http
	}

	return nil
}

func (p *CoreSkillPlugin) GetExecutors() []executor.StepExecutor {
	// Return stub executors - cortex will provide implementations
	// The actual executor implementations are in cortex and are
	// registered separately when the plugin is loaded
	return []executor.StepExecutor{
		// Control flow
		&stubExecutor{nodeType: "if"},
		&stubExecutor{nodeType: "switch"},
		&stubExecutor{nodeType: "delay"},

		// Data operations
		&stubExecutor{nodeType: "transform"},
		&stubExecutor{nodeType: "set"},
		&stubExecutor{nodeType: "merge"},
		&stubExecutor{nodeType: "filter"},
		&stubExecutor{nodeType: "sort"},
		&stubExecutor{nodeType: "aggregate"},
		&stubExecutor{nodeType: "split"},
		&stubExecutor{nodeType: "join"},
		&stubExecutor{nodeType: "loop"},

		// Actions
		&stubExecutor{nodeType: "http"},
		&stubExecutor{nodeType: "code"},
		&stubExecutor{nodeType: "ai"},
		&stubExecutor{nodeType: "pgvector"},
		&stubExecutor{nodeType: "invoke_agent"},

		// Communication
		&stubExecutor{nodeType: "slack"},
		&stubExecutor{nodeType: "discord"},
		&stubExecutor{nodeType: "teams"},
		&stubExecutor{nodeType: "email"},

		// Tools
		&stubExecutor{nodeType: "tool_pgvector"},
		&stubExecutor{nodeType: "tool_debug"},
		&stubExecutor{nodeType: "tool_memory"},

		// Triggers
		&stubExecutor{nodeType: "webhook"},
		&stubExecutor{nodeType: "webhook_response"},
		&stubExecutor{nodeType: "cron"},
		&stubExecutor{nodeType: "manual"},
	}
}

func (p *CoreSkillPlugin) Shutdown() error {
	return nil
}

// stubExecutor is a placeholder that cortex replaces with real implementations
type stubExecutor struct {
	nodeType string
}

func (e *stubExecutor) Type() string {
	return e.nodeType
}

func (e *stubExecutor) Execute(ctx context.Context, step *executor.StepDefinition, resolver executor.TemplateResolver) (*executor.StepResult, error) {
	// This should never be called - cortex provides real implementations
	return &executor.StepResult{
		Output: map[string]interface{}{
			"error": "stub executor - cortex should provide real implementation",
		},
	}, nil
}

// Plugin symbol that cortex will load
var Plugin skill.SkillPlugin = &CoreSkillPlugin{}