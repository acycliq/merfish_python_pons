import numpy as np
import pandas as pd
from .utils import is_inside_sm_parallel
from .utils import transformation, check_path
from .config import *
from pathlib import Path
from .base_logger import logger


def app(cfg):
    """
    calcs the ROI-specific cell by gene matrix
    :return:
    """

    # Transformation from micron to pixel coords
    tx, ty, _, _ = transformation(cfg)

    # get the (unrotated) ROI polygon. This is in pixels
    roi = cfg['clip_poly']

    # make sure roi is a list
    roi = [list(d) for d in roi]

    # make sure the polygon is a closed one.
    if tuple(roi[0]) != tuple(roi[-1]):
        roi.append(roi[0])

    # cell centroids (full slice)
    cell_meta = pd.read_csv(cfg['cell_metadata']).rename(columns={"Unnamed: 0": "cell_id"})
    centroids_df = cell_meta[['cell_id', 'center_x', 'center_y']]

    # express the centroids in pixel coordinates
    centroids_df = centroids_df.assign(center_x_px=tx(centroids_df.center_x.values))
    centroids_df = centroids_df.assign(center_y_px=ty(centroids_df.center_y.values))

    # get the cells and keep only those whose centroid is within the ROI poly
    centroids = centroids_df[['center_x_px', 'center_y_px']].values
    mask = is_inside_sm_parallel(centroids, np.array(roi))
    roi_cell_ids = centroids_df.cell_id.values[mask]

    # get now the cell-by-gene array (for the full slice)
    cell_by_gene = pd.read_csv(cfg['cell_by_gene']).rename(columns={"Unnamed: 0": "cell_id"})
    cell_by_gene = cell_by_gene.set_index('cell_id')

    # truncate the df and keep only cells inside the ROI
    out = cell_by_gene.loc[roi_cell_ids]
    out.index.name = ''

    return out


def save_df(df, fName):
    parent_dir = Path(fName).parent.absolute()
    check_path(str(parent_dir))
    df.to_csv(fName)
    logger.info('Saved at: %s' % fName)


if __name__ == "__main__":
    slice_ids = [
        "MsBrain_Eg1_VS6_JH_V6_05-02-2021",
        "MsBrain_Eg2_VS6_V11_JH_05-02-2021",
        "MsBrain_Eg3_VS6_JH_V6_05-01-2021",
        "MsBrain_EG4_VS6library_V6_LH_04-14-21",
        "MsBrain_Eg5_VS6_JH_V6_05-16-2021",
        "VS6_MsBrain_B3_VS6library_V10_LH_02-07-21",

        "MsBrain_ZM0_VS6_JH_V6_05-15-2021",
        "MsBrain_ZM1_VS6_JH_V11_05-16-2021",
        "MsBrain_ZM2_VS6_JH_V11_05-15-2021",
        "MsBrain_ZM3_VS6_JH_V11_05-17-2021",
        "MsBrain_ZM4_VS6_JH_V11_05-11-2021",
        "MsBrain_ZM5.1_VS6_JH_V11_05-12-2021",
        "MsBrain_ZM5.2_VS6_JH_V6_05-13-2021",
        "MsBrain_ZM6.1_VS6_V6_JH_05-11-2021",
        "MsBrain_ZM7.1_VS6_V6_JH_05-12-2021",
        "MsBrain_ZM7.2_VS6_JH_V11_05-13-2021",

        ]

    region_ids = ['region_0', 'region_1']
    z_stacks = [0, 1, 2, 3, 4, 5, 6];

    for slice_id in slice_ids:
        for region_id in region_ids:
            cfg = config.get_config(merfish_id="", slice_id=slice_id, region_id=region_id)
            df = app(cfg)
            save_df(df, os.path.join(cfg['target_dir'], 'roi_cell_by_gene', 'roi_cell_by_gene.csv'))