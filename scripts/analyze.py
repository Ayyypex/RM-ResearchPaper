import pandas as pd
import seaborn as sns
import scipy.stats as stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Load the CSV data into a pandas DataFrame
df = pd.read_csv('data/dataset.csv')

############ DESCRIPTIVE STATISTICS ############

# Encode the binary 'merged' column
df['merged_encoded'] = df['merged'].map({False: 0, True: 1})

# Compute descriptive statistics
stats_all = df.describe()
stats_merged = df[df['merged_encoded'] == 1].describe()
stats_not_merged = df[df['merged_encoded'] == 0].describe()

# Write statistics to file
with open('results/descriptive_statistics.txt', 'w') as f:
    f.write("Descriptive Statistics (All):\n")
    f.write(stats_all.to_string())
    f.write("\n\n\nDescriptive Statistics (Merged):\n")
    f.write(stats_merged.to_string())
    f.write("\n\n\nDescriptive Statistics (Not Merged):\n")
    f.write(stats_not_merged.to_string())

    # Iterate over each unique author_association
    for author_association_type in df['author_association'].unique():
        # Filter data based on 'author_association' column
        df_author = df[df['author_association'] == author_association_type]

        # Compute descriptive statistics
        stats_author = df_author.describe()
        
        # Write to file
        f.write(f"\n\n\nDescriptive Statistics (Author Association: {author_association_type}):\n")
        f.write(stats_author.to_string())

# Drop encoded column as it is not needed later
df.drop('merged_encoded', axis=1, inplace=True)

############ DESCRIPTIVE STATISTICS ############


############ CORRELATION MATRIX ############

# Create a dictionary mapping author associations to encoded values. Ordered by 'closeness' to the project
mapping = {'NONE': 0, 'CONTRIBUTOR': 1, 'COLLABORATOR': 2, 'MEMBER': 3}

# Use the map() method to replace the values in the 'author_association' column
df['author_association'] = df['author_association'].map(mapping)

# Compute correlation matrix
corr_matrix = df.corr()
corr_matrix_str = corr_matrix.to_string()
with open('results/correlation_matrix.txt', 'w') as f:
    f.write("Correlation Matrix:\n")
    f.write(corr_matrix_str)

# Create and save heatmap of the correlation matrix
plt.figure(figsize=(22, 16))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix Heatmap', fontsize=32)
plt.tight_layout() 
plt.savefig('results/heatmap.png')
plt.close()

############ CORRELATION MATRIX ############


############ SCATTER PLOTS FOR TIME TO MERGE ############

# Filter data based on 'merged' column
df_merged = df[df['merged'] == True]

# Define lists for independent variable names and titles
independent_vars = ['description_length', 'time_to_first_response', 'num_comments', 'num_review_comments',
                    'num_commits', 'num_additions', 'num_deletions', 'num_changed_lines', 'num_changed_files']

titles = ['Description Length', 'Time to First Response', 'Number of Comments', 'Number of Review Comments',
          'Number of Commits', 'Number of Additions', 'Number of Deletions', 'Number of Changed Lines', 'Number of Changed Files']

# Loop through independent variables and titles to create scatter plots
for i in range(len(independent_vars)):
    # Create scatter plot
    plt.scatter(df_merged[independent_vars[i]], df_merged['time_to_merge'])
    plt.xlabel(titles[i])
    plt.ylabel('Time to Merge')
    plt.title(f'Scatter Plot: {titles[i]} vs. Time to Merge')
    
    # Save scatter plot
    plt.savefig(f'results/scatter_plots/{independent_vars[i]}.png')
    
    # Clear the plot for the next iteration
    plt.clf()

############ SCATTER PLOTS FOR TIME TO MERGE ############


############ LINEAR REGRESSION FOR TIME TO MERGE ############

# Filter data based on 'merged' column
df_merged = df[df['merged'] == True]

# Create linear regression model for time_to_merge to calculate coefficients and intercept
X1 = df_merged[[ 'description_length', 'time_to_first_response', 'num_comments', 'num_review_comments',
                 'num_commits', 'num_additions', 'num_deletions', 'num_changed_lines', 'num_changed_files' ]]
y = df_merged['time_to_merge']
model1 = LinearRegression()
model1.fit(X1, y)

# Create separate model to calculate p-values
X2 = sm.add_constant(X1)     # Add a constant term to the predictor variables to account for the intercept
model2 = sm.OLS(y, X2).fit() # Fit the linear regression model
p_values = model2.pvalues    # Extract the p-values for the coefficients

# Write results to file
with open('results/linear_regression.txt', 'w') as f:
    f.write("Time to Merge Linear Regression Coefficients:\n")
    for i, key in enumerate(X1.keys()):
        f.write(f'\t{key}: {model1.coef_[i]}\n')
    f.write("\nTime to Merge Linear Regression Intercept:")
    f.write(str(model1.intercept_))
    f.write("\n\nP-values:\n")
    f.write(str(p_values))

############ LINEAR REGRESSION FOR TIME TO MERGE ############


############ CHI-SQUARED TESTS FOR MERGE DECISION ############

# Reset the file by opening it in write mode
with open('results/chi_squared_tests.txt', 'w') as f:
    f.write("")

# Loop through independent variables to perform chi-squred tests
for var in independent_vars:
    # Create contingency table
    contingency_table = pd.crosstab(df[var], df['merged'])

    # Perform chi-squared test
    chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)

    # Create a string with the results
    results_str = "Results for column '{}':\n".format(var)
    results_str += "Chi-squared statistic: {:.2f}\n".format(chi2)
    results_str += "p-value: {:.4f}\n".format(p_val)
    results_str += "Degrees of freedom: {}\n".format(dof)

    # Write results to file
    with open('results/chi_squared_tests.txt', 'a') as f:
        f.write(results_str)
        f.write("\n")

############ CHI-SQUARED TESTS FOR MERGE DECISION ############