import yaml 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from PIL import Image


class WellTimeSeries:
    '''
    This class reads the timeseries for a well and creates a 3D diagram
    '''
    def __init__(self, init_folder): 
        '''
        init_folder: the folder that contains the metadata yaml file and the csv file of each reading
        '''
        #loads the metadata file
        self.init_folder = init_folder
        with open(f'{init_folder}/metadata.yaml', 'r') as file:
            self.config_data = yaml.safe_load(file) 
        self.readings = {}
        self.max = 0
        max = 0
        #creates a dictionary containing a dataframe with the CSV file data for each timestamp
        for timestamp, file  in self.config_data["series"].items():
            df = pd.read_csv(f'{init_folder}/{file}', header=0, index_col=0)
            df = self.remove_outliers_corner(df)
            max = df.values.max()
            if max > self.max:
                self.max=max
            self.readings[timestamp]= df
        self.plotted_heatmaps = []

    def remove_outliers_z(self, df):
        flat_values = df.values.flatten()
        # Calculate the overall mean and standard deviation
        mean = np.mean(flat_values)
        std_dev = np.std(flat_values)
        # Calculate Z-scores for all values in the DataFrame
        z_scores = (df - mean) / std_dev
        # Set a threshold for Z-scores (e.g., 3)
        threshold = 3
        # Create a mask for values within the threshold
        mask = np.abs(z_scores) < threshold
        # Apply the mask to keep only values within the threshold
        df_no_outliers = df[mask]
        return df_no_outliers
    
    def remove_outliers_corner(self, df):
        df.iloc[42,0] = 0
        df.iloc[43,0] = 0
        df.iloc[43,1] = 0
        df.iloc[43,2] = 0
        df.iloc[44,0] = 0
        df.iloc[44,1] = 0
        df.iloc[44,2] = 0
        df.iloc[45,0] = 0
        df.iloc[45,1] = 0
        df.iloc[45,2] = 0
        df.iloc[45,3] = 0
        return df


    def plot_heatmaps(self):
        for timestamp, df in self.readings.items():
            well_name = self.config_data["well_name"]
            ax=plt.axes()
            sns.heatmap(df, cmap="icefire", ax=ax, vmax=self.max)
            #sns.heatmap(df, cmap="icefire",  ax=ax, vmax=1000)

            ax.set_title(f'Measurement {timestamp}')
            # Adjust the x and y ticks to make them less dense
            ax.set_xticks(ax.get_xticks()[::5])  
            ax.set_yticks(ax.get_yticks()[::5])  
            heatmap_path = f'{well_name}/file_{timestamp}'
            self.plotted_heatmaps.append(heatmap_path)
            plt.savefig(heatmap_path,dpi=400)
            plt.close()
    
    

    def make_gif(self):
        # Load images
        images = [Image.open(f'{img}.png') for img in self.plotted_heatmaps]
        gif_path = self.init_folder +'timeseries.gif'
        images[0].save(
            gif_path,
            save_all=True,
            append_images=images[1:],
            duration=400,  # Duration between frames in milliseconds
            loop=0  # Loop forever
            )

if __name__ == "__main__":
    with open('well_names.yaml', 'r') as file:
        total_wells = yaml.safe_load(file)
    for well in total_wells:        
        well = WellTimeSeries(f'./{well}')
        # well.plot_heatmaps()
        well.make_gif()