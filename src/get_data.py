# ==============================================================================
# get_data.py
#
# Retrieve wave observation and forecast files.
#
# ==============================================================================
import urllib.request


def download_file(url, local_file):
    '''
    Download a file from a URL.

    Parameters
    -----------
    url : str
        URL of the file to download.
    local_file : pathlib Path object
        What to name the downloaded file. Can include directory tree.

    Returns
    --------
    str
        Path of the downloaded file.
    '''
    try:
        parent_dirs = local_file.parent
    except AttributeError:
        local_file = Path(local_file)
        parent_dirs = local_file.parent

    if not parent_dirs.exists():
        parent_dirs.mkdir()

    filename, headers = urllib.request.urlretrieve(url, local_file)

    return filename


def parse_cdip_url(buoy_num, dataset, product, *kwargs):
    '''
    Parse the URL for the desired CDIP netcdf file.

    Parameters
    -----------
    buoy_num : int or str
        Unique buoy identification number.
    dataset : str
        CDIP dataset.
        'obs' for observation data, 'model' for forecast model output.
    product : str
        CDIP product.
        'xy' for buoy x & y data, 'rt' for ???

    Returns
    --------
    str
        CDIP URL.
    '''
    base_url = 'https://thredds.cdip.ucsd.edu/thredds/fileServer/cdip/'
    valid_prods_obs = ['xy', 'rt']
    valid_prods_mdl = ['hindcast', 'nowcast', 'forecast']

    dataset_base = dataset.split('-')[0]

    if dataset_base == 'obs':
        if product in valid_prods_obs:
            suffix = '/realtime/{}p1_{}.nc'
            suffix = suffix.format(buoy_num, product)
            cdip_url = base_url + suffix
        else:
            msg = 'Invalid CDIP realtime product "{}"'.format(product)
            raise ValueError(msg)
    elif dataset_base == 'model':
        cdip_url = _parse_cdip_url_mdl(base_url, buoy_num, dataset, product, *kwargs)

    return cdip_url


def _parse_cdip_url_mdl(base_url, buoy_num, dataset, product, *kwargs):
    '''
    Parse the URL for a CDIP forecast model output file.

    Parameters
    -----------
    base_url : str
        Base CDIP thredds url.
    buoy_num : str or int
        Unique buoy identification number
    dataset : str
        CDIP dataset.
    product : str
        CDIP model product.
    kwargs: keyword args

    Returns
    --------
    str
        CDIP model product URL.

    Notes
    ------
    - Datasets: 'validation', 'grids', 'alongshore'
    - Products:
        - All datasets: 'hindcast', 'nowcast', 'forecast'
        - Grids only: 'spectra'
    '''
    base_url = base_url + 'model/'

    _, dset_type = dataset.split('-')

    if dset_type == 'grids':
        if product == 'spectra':
            suffix = 'MOP_grids/{}_nowcast_{}.nc'
            # region, product
        else:
            suffix = 'MOP_grids/{}_{}_{}.nc'
            # Region, resolution, product - SL_0.002_seaswellfc.nc
            # or socal_nowcast_spectra.nc
    elif dset_type == 'alongshore':
        if kwargs.region in ['socal', 'norcal']:
            suffix = 'MOP_alongshore/{}_alongshore_{}.nc'
            # region, product - norcal_alongshore_forecast.nc
        else:
            suffix = 'MOP_alongshore/VE{}_{}.nc'
            # buoy num, product - VE674_nowcast.nc
    elif dset_type == 'validation':
        suffix = 'MOP_validation/BP{}_{}.nc'
        # buoy num, product
    else:
        msg = 'Invalid CDIP model URL parameters'
        raise ValueError(msg)
    cdip_url = root_url + suffix

    return cdip_url
