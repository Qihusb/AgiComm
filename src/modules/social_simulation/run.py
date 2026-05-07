from experiment_controller import ExperimentController, run_multiple_experiments

def main():
    # 示例配置
    config = {
        'data_path': "../../../data/processed/netizen_science_standardized_profiles.csv",
        'seed_strategy': 'influence',  # 'random', 'influence', 'emotion'
        'num_seeds': 5,
        'max_steps': 10,
        'user_filter': {
            'emotion_threshold': 0.3,
            'stance_range': [-1, 1],
            'influence_threshold': 0.1
        },
        'visualize': True,
        'experiment_name': 'baseline_experiment'
    }

    # 运行单个实验
    controller = ExperimentController(config)
    controller.setup_experiment()
    result = controller.run_experiment()

    print("\n=== Single Experiment Result ===")
    print("Seeds:", result['seeds'])
    print("Propagation history:", result['history'])
    print("Final active nodes:", len(result['active_nodes']))
    print("Metrics:", result['metrics'])

    # 运行多个实验对比
    configs = [
        {**config, 'seed_strategy': 'influence', 'experiment_name': 'influence_seeds'},
        {**config, 'seed_strategy': 'random', 'experiment_name': 'random_seeds'},
        {**config, 'seed_strategy': 'emotion', 'experiment_name': 'emotion_seeds'}
    ]

    results = run_multiple_experiments(configs)

    print("\n=== Multiple Experiments Comparison ===")
    for i, result in enumerate(results):
        print(f"Experiment {i+1}: {configs[i]['experiment_name']}")
        print(f"  Final size: {result['metrics']['final_size']}")
        print(f"  Coverage rate: {result['metrics']['coverage_rate']:.2%}")
        print(f"  Polarization index: {result['metrics']['polarization_index']:.3f}")
        print()

if __name__ == "__main__":
    main()