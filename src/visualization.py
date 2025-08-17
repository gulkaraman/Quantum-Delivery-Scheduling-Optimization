import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go


def print_comparison_table(results):
    df = pd.DataFrame(results).T
    print(df)
    return df


def plot_gantt_chart(schedule, title="Gantt Chart", save_path=None):
    df = pd.DataFrame(schedule)
    df['Start'] = df['timeslot']
    df['Finish'] = df['timeslot'] + 1
    df['Resource'] = df['courier_id'].astype(str)
    fig = go.Figure()
    colors = sns.color_palette('tab20', n_colors=df['Resource'].nunique()).as_hex()
    for i, (courier, group) in enumerate(df.groupby('Resource')):
        fig.add_trace(go.Bar(
            x=group['Finish'] - group['Start'],
            y=group['package_id'],
            base=group['Start'],
            orientation='h',
            name=f'Courier {courier}',
            marker_color=colors[i % len(colors)],
            hovertext=[f"Package {p}, Time {t}" for p, t in zip(group['package_id'], group['timeslot'])]
        ))
    fig.update_layout(barmode='stack', title=title, xaxis_title='Time', yaxis_title='Package', legend_title='Courier', height=500)
    if save_path:
        fig.write_image(save_path)
    fig.show()


def plot_qubo_heatmap(qubo, title="QUBO Heatmap", save_path=None):
    keys = list(qubo.keys())
    labels = sorted(set([k[0] for k in keys] + [k[1] for k in keys]))
    size = len(labels)
    mat = np.zeros((size, size))
    idx_map = {k: i for i, k in enumerate(labels)}
    for (i, j), v in qubo.items():
        mat[idx_map[i], idx_map[j]] = v
    plt.figure(figsize=(12, 10))
    ax = sns.heatmap(mat, cmap='coolwarm', xticklabels=labels, yticklabels=labels, cbar_kws={'label': 'QUBO Value'}, annot=False)
    plt.title(title)
    plt.xlabel('Variable')
    plt.ylabel('Variable')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()


def plot_runtime_comparison(results, save_path=None):
    df = pd.DataFrame(results).T
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(x=df.index, y='runtime', data=df, hue=df.index, palette='viridis', legend=False)
    plt.ylabel('Runtime (s)')
    plt.title('Solver Runtime Comparison')
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.3f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 3), textcoords='offset points')
    if save_path:
        plt.savefig(save_path)
    plt.show()


def plot_constraint_violations(results, save_path=None):
    df = pd.DataFrame(results).T
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(x=df.index, y='violations', data=df, hue=df.index, palette='magma', legend=False)
    plt.ylabel('Constraint Violations')
    plt.title('Constraint Satisfaction Comparison')
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height()) if not np.isnan(p.get_height()) else "-"}', (p.get_x() + p.get_width() / 2., p.get_height() if not np.isnan(p.get_height()) else 0),
                    ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 3), textcoords='offset points')
    if save_path:
        plt.savefig(save_path)
    plt.show()


def plot_metrics_comparison(results, save_path=None):
    df = pd.DataFrame(results).T
    metrics = ['makespan', 'energy', 'runtime', 'violations']
    df_metrics = df[metrics].copy()
    df_metrics = df_metrics.reset_index().melt(id_vars='index', value_vars=metrics, var_name='Metric', value_name='Value')
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x='index', y='Value', hue='Metric', data=df_metrics)
    plt.title('Solver Metrics Comparison')
    plt.xlabel('Solver')
    plt.ylabel('Value')
    plt.legend(title='Metric')
    for p in ax.patches:
        height = p.get_height()
        if not np.isnan(height):
            ax.annotate(f'{height:.2f}', (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=9, color='black', xytext=(0, 3), textcoords='offset points')
    if save_path:
        plt.savefig(save_path)
    plt.show()


def plot_solution_tables(results):
    for solver, res in results.items():
        if res['schedule']:
            print(f"\n--- Solution Table: {solver} ---")
            df = pd.DataFrame(res['schedule'])
            print(df)


def plot_feasibility(results):
    df = pd.DataFrame(results).T
    df['feasible'] = df['violations'].apply(lambda v: v == 0 if v is not None else False)
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(x=df.index, y='feasible', data=df, hue=df.index, palette='Set2', legend=False)
    plt.ylabel('Feasibility (1=True, 0=False)')
    plt.title('Solver Feasibility Comparison')
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 3), textcoords='offset points')
    plt.show()


def plot_solution_quality(results):
    df = pd.DataFrame(results).T
    if 'energy' in df.columns:
        plt.figure(figsize=(8, 5))
        ax = sns.boxplot(data=df[['energy', 'makespan', 'runtime']].dropna())
        plt.title('Solution Quality Distribution (Energy, Makespan, Runtime)')
        plt.show()


def critical_analysis(results):
    df = pd.DataFrame(results).T
    best = df.sort_values(['violations', 'makespan', 'runtime']).iloc[0]
    print(f"Best solver: {best.name}\nReason: Least constraint violation, lowest makespan and/or fastest runtime.")
    print(best)
    return best 