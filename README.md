**http-coll-data-server** (HCDS) is designed to be the web interface to outcomes of hydrodynamical simulations of planetary collisions. It serves at a data backend to make interactive web sites.

## Requirements

The following Python packages are needed to make the library work:
* numpy
* pytables
* matplotlib
* mpl_tune (available either as `mpl-tune` pip package or [on Github](https://github.com/aemsenhuber/mpl_tune))
* collresolve (available on [on Github](https://github.com/aemsenhuber/collresolve))

## Configuration

The configuration file is `hcds_config.py`. The different configuration options and their documentation are listed there.

## Running

To start the web server, execute the `main.py` file, with, e.g.,
```
python main.py
```

## License

The library is licensed under version 2.0 of the Apache License, see the `LICENSE` file for the full terms and conditions.

