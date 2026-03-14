//go:build plugin

package main

import (
	"github.com/axiom-studio/cortex/pkg/agent/executor"
	"github.com/axiom-studio/cortex/pkg/agent/module"
	"go.uber.org/zap"
	"k8s.io/client-go/kubernetes"
)

// CoreSkillPlugin implements the SkillPlugin interface
type CoreSkillPlugin struct {
	logger     *zap.SugaredLogger
	k8sClient  kubernetes.Interface
	httpClient interface{} // *http.Client
}

func (p *CoreSkillPlugin) Initialize(config map[string]interface{}) error {
	// Extract dependencies from config
	if logger, ok := config["logger"].(*zap.SugaredLogger); ok {
		p.logger = logger
	}

	if k8s, ok := config["k8s-client"].(kubernetes.Interface); ok {
		p.k8sClient = k8s
	}

	if http, ok := config["http-client"]; ok {
		p.httpClient = http
	}

	return nil
}

func (p *CoreSkillPlugin) GetExecutors() []executor.StepExecutor {
	executors := []executor.StepExecutor{
		// Control flow - directly from executor package
		&executor.IfExecutor{},
		&executor.SwitchExecutor{},
		&executor.DelayExecutor{},

		// Data operations
		&executor.TransformExecutor{},
		&executor.SetExecutor{},
		&executor.MergeExecutor{},
		executor.NewFilterExecutor(),
		executor.NewSortExecutor(),
		executor.NewAggregateExecutor(),
		executor.NewSplitExecutor(),
		executor.NewJoinExecutor(),
		executor.NewLoopExecutor(),

		// Actions
		executor.NewHTTPExecutor(),
		executor.NewAIExecutor(),
		executor.NewPGVectorExecutor(),

		// Communication
		executor.NewSlackExecutor(),
		executor.NewDiscordExecutor(),
		executor.NewTeamsExecutor(),
		executor.NewEmailExecutor(),
	}

	// Add code executor if k8s client available
	if p.k8sClient != nil {
		codeConfig := &executor.CodeExecutorConfig{
			Namespace:               module.GetAgentsNamespace(),
			RunnerImage:             module.GetCodeExecutorImage(),
			ServiceAccount:          "default",
			TTLSecondsAfterFinished: module.GetJobTTLSecondsAfterFinished(),
		}
		executors = append(executors, executor.NewCodeExecutor(p.k8sClient, codeConfig))
	}

	return executors
}

func (p *CoreSkillPlugin) Shutdown() error {
	// Cleanup if needed
	return nil
}

// Plugin symbol that cortex will lookup
var Plugin = &CoreSkillPlugin{}
