import matplotlib.pyplot as plt
import numpy as np

def plot_results(history, metrics, experiment_name="experiment"):
    """
    可视化输出（Visualization）
    核心逻辑：
    把指标变成图，而不是数字
    例如：
    传播曲线（step → 覆盖人数）
    情感演化曲线
    立场分布变化
    本质：把结果变成"可解释证据"（论文用）
    """

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'Social Simulation Results - {experiment_name}', fontsize=16)

    # 1. 传播曲线
    axes[0, 0].plot(history, marker='o', linewidth=2, markersize=6)
    axes[0, 0].set_title('Propagation Curve')
    axes[0, 0].set_xlabel('Step')
    axes[0, 0].set_ylabel('Active Nodes')
    axes[0, 0].grid(True, alpha=0.3)

    # 添加关键指标标注
    final_size = metrics['final_size']
    steps = metrics['steps']
    axes[0, 0].axhline(y=final_size, color='r', linestyle='--', alpha=0.7, label=f'Final Size: {final_size}')
    axes[0, 0].axvline(x=steps-1, color='g', linestyle='--', alpha=0.7, label=f'Steps: {steps}')
    axes[0, 0].legend()

    # 2. 立场分布对比
    active_stance = metrics['active_stance_mean']
    inactive_stance = metrics['inactive_stance_mean']
    active_var = metrics['active_stance_var']
    inactive_var = metrics['inactive_stance_var']

    stances = ['Active Nodes', 'Inactive Nodes']
    means = [active_stance, inactive_stance]
    variances = [active_var, inactive_var]

    x = np.arange(len(stances))
    width = 0.35

    bars1 = axes[0, 1].bar(x - width/2, means, width, label='Mean Stance', alpha=0.8)
    bars2 = axes[0, 1].bar(x + width/2, variances, width, label='Stance Variance', alpha=0.8)

    axes[0, 1].set_title('Stance Distribution Comparison')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(stances)
    axes[0, 1].set_ylabel('Value')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # 添加数值标签
    for bar in bars1:
        height = bar.get_height()
        axes[0, 1].text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}', ha='center', va='bottom')

    for bar in bars2:
        height = bar.get_height()
        axes[0, 1].text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}', ha='center', va='bottom')

    # 3. 情感对比
    active_emotion = metrics['active_emotion_mean']
    inactive_emotion = metrics['inactive_emotion_mean']

    emotions = [active_emotion, inactive_emotion]
    labels = ['Active Nodes', 'Inactive Nodes']

    axes[1, 0].bar(labels, emotions, color=['skyblue', 'lightcoral'], alpha=0.8)
    axes[1, 0].set_title('Emotion Intensity Comparison')
    axes[1, 0].set_ylabel('Mean Emotion')
    axes[1, 0].grid(True, alpha=0.3)

    # 添加数值标签
    for i, v in enumerate(emotions):
        axes[1, 0].text(i, v + 0.01, f'{v:.2f}', ha='center', va='bottom')

    # 4. 关键指标汇总
    axes[1, 1].axis('off')
    metrics_text = ".2f"".2f"".2f"".2f"".2f"".2f"f"""
    Coverage Rate: {metrics['coverage_rate']:.2%}
    Average Growth Rate: {metrics['avg_growth_rate']:.3f}
    Max Growth Rate: {metrics['max_growth_rate']:.3f}
    Polarization Index: {metrics['polarization_index']:.3f}
    Avg Influence (Active): {metrics['avg_influence_active']:.3f}
    Avg Activeness (Active): {metrics['avg_activeness_active']:.3f}
    """

    axes[1, 1].text(0.1, 0.9, metrics_text, transform=axes[1, 1].transAxes,
                   fontsize=10, verticalalignment='top', fontfamily='monospace',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    plt.savefig(f'{experiment_name}_results.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_multiple_experiments(results_list, experiment_names):
    """绘制多个实验对比"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # 传播曲线对比
    for i, (result, name) in enumerate(zip(results_list, experiment_names)):
        axes[0].plot(result['history'], label=name, marker='o', linewidth=2)

    axes[0].set_title('Propagation Curves Comparison')
    axes[0].set_xlabel('Step')
    axes[0].set_ylabel('Active Nodes')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 最终规模对比
    final_sizes = [r['metrics']['final_size'] for r in results_list]
    axes[1].bar(experiment_names, final_sizes, alpha=0.8)
    axes[1].set_title('Final Propagation Size Comparison')
    axes[1].set_ylabel('Final Active Nodes')
    axes[1].grid(True, alpha=0.3)

    # 添加数值标签
    for i, v in enumerate(final_sizes):
        axes[1].text(i, v + 0.01, str(v), ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('experiments_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()