import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def make_corr_matrix(data_for_corr, sdq_subscales, facets_cols, file_name_prefix=""):
    corr_mat = data_for_corr.corr().loc[facets_cols, sdq_subscales].sort_values("tot", ascending=False)
    corr_mat.to_csv(f"output/corr_mat{file_name_prefix}.csv", float_format='%.2f')

def make_scatter_plots(data, sdq_subscales, facets_cols, file_name_prefix=""):
    # Grouped scatter plots

    fig, axs = plt.subplots(len(facets_cols), len(sdq_subscales), figsize=(30, 100))  # 3 subplots side by side
    
    for i, facets_col in enumerate(facets_cols):
        for j, sdq_subscale in enumerate(sdq_subscales):
            axs[i, j].scatter(data[facets_col], data[sdq_subscale])
            axs[i, j].set_xlabel(facets_col)
            axs[i, j].set_ylabel(sdq_subscale)
    
    fig.subplots_adjust(hspace=0.4, wspace=0.4)
    axs = axs.flatten()

    # Set ylim
    for ax in axs:
        ax.set_xlim([0, 1.0])

    plt.tight_layout()

    #plt.tight_layout()
    plt.savefig(f"plots/scatter{file_name_prefix}.png")

def plot_histograms_facets(data, facets_cols, file_name_prefix=""):
    # Distribution of each FACETS item
    fig, axs = plt.subplots(len(facets_cols), 1, figsize=(6, 150))  # 3 subplots side by side
    
    for i, facets_col in enumerate(facets_cols):
        counts, bins, _ = axs[i].hist(data[facets_col])
        axs[i].set_xlabel(facets_col)

        axs[i].set_xlim([0, 1])

        # Calculate mean and standard deviation
        mean = np.mean(data[facets_col])
        median = np.median(data[facets_col])
        std_dev = np.std(data[facets_col])

        # Plot lines for 1 and 2 standard deviations
        axs[i].axvline(mean, color='b', linestyle='--', label='Mean')
        axs[i].axvline(median, color='b', linestyle='-', label='Median')
        axs[i].axvline(mean - std_dev, color='y', linestyle='--', label='-1 SD')
        axs[i].axvline(mean + std_dev, color='y', linestyle='--', label='+1 SD')
        axs[i].axvline(mean - 2*std_dev, color='y', linestyle='--', label='-2 SD')
        axs[i].axvline(mean + 2*std_dev, color='y', linestyle='--', label='+2 SD')


    fig.subplots_adjust(hspace=0.4, wspace=0.4)
    axs = axs.flatten()

    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    plt.tight_layout()

    #plt.tight_layout()
    plt.savefig(f"plots/facet_histograms{file_name_prefix}.png")

def multiple_regression(data, sdq_subscales, facets_cols, file_name_prefix=""):
    import statsmodels.api as sm
    for subscale in sdq_subscales:
        print(subscale)
        mod = sm.OLS(data[subscale], data[facets_cols])
        result = mod.fit()

        with open(f"output/ols_{subscale}{file_name_prefix}.csv", 'w') as f:
            f.write(result.summary().as_csv())

if __name__ == "__main__":

    data = pd.read_csv("data/merged.csv", index_col=0)

    description = data.describe()
    description.to_csv("output/description.csv")

    # non_num_cols = [
    #     "Entry ID", "Actor type", "Subject ID", "Study ID", "Group ID",
    #     "anonymised ID", "Time", "Subject-Respondent Pair ID"
    # ]
    data_for_corr = data.drop("Study ID", axis=1)
    print(data_for_corr.columns)

    sdq_subscales = ["emotion", "conduct", "hyper", "peer",	"prosoc", "tot"]
    facets_cols = [x for x in data_for_corr.columns if "_" in x] + ["toileting"]
    sdq_item_cols = [x for x in data_for_corr.columns if x not in facets_cols and x not in sdq_subscales]
    
    make_corr_matrix(data_for_corr, sdq_subscales, facets_cols)
    #make_scatter_plots(data, sdq_subscales, facets_cols)
    #plot_histograms_facets(data_for_corr, facets_cols)
    multiple_regression(data, sdq_subscales, facets_cols)

    data_split_by_anchors = pd.read_csv("data/merged_split_by_anchor.csv")
    data_split_by_anchors = data_split_by_anchors.drop("Study ID", axis=1)
    facets_cols_split = [x for x in data_split_by_anchors.columns if "_" in x]
    make_corr_matrix(data_split_by_anchors, sdq_subscales, facets_cols_split, file_name_prefix="_split")
    multiple_regression(data_split_by_anchors, sdq_subscales, facets_cols_split, file_name_prefix="_split")
