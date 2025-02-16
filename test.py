import pandas as pd
import matplotlib.pyplot as plt

# Sample DataFrame
df = pd.DataFrame({
    'x': [1, 2, 3, 4, 5],
    'y': [10, 20, 15, 25, 30]
}, index=['A', 'B', 'C', 'D', 'E'])  # Index as labels

# Create scatter plot
plt.figure(figsize=(8, 5))
plt.scatter(df['x'], df['y'], color='blue')

# Add labels from index
for i, txt in enumerate(df.index):
    plt.text(df['x'][i], df['y'][i], txt, fontsize=12, ha='right', va='bottom')

plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("Scatter Plot with Index Labels")
plt.show()
