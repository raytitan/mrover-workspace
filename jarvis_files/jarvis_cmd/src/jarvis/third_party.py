import os
import shutil


def check_lcm(ctx):
    """
    Checks for the existence of LCM in the product venv.
    """
    # check for lcm-gen in both venvs
    if (not os.path.exists(ctx.get_product_file('bin', 'lcm-gen')) or
            not os.path.exists(ctx.get_jarvis_file('bin', 'lcm-gen'))):
        return False

    # check for liblcm.so
    libname = 'liblcm.so'

    if not os.path.exists(ctx.get_product_file('lib', libname)):
        return False

    # check that lcm can be imported in Python inside product venv
    with ctx.inside_product_env():
        try:
            ctx.run("python -c 'import lcm'", hide='both')
        except:
            return False

    return True


def ensure_lcm(ctx):
    """
    Installs LCM into the product venv. LCM is expected to be included as a
    git submodule or a subdirectory in the third-party directory.

    Also installs lcm-gen into the Jarvis venv.
    """
    if check_lcm(ctx):
        print("[jarvis] lcm found")
        return

    lcmdir = os.path.join(ctx.third_party_root, 'lcm')
    with ctx.intermediate('lcm'):
        print("[jarvis] lcm not found, installing")
        print("[jarvis][lcm] Retrieving source from {}".format(ctx.product_env))
        ctx.run("cp -r \"{}\"/* .".format(lcmdir))  # TODO: Use python's own cp
        print("[jarvis][lcm] Running bootstrap.sh...")
        ctx.run("./bootstrap.sh")
        print("[jarvis][lcm] Running configure.sh...")
        ctx.run("./configure --prefix={}".format(ctx.product_env))
        print("[jarvis][lcm][make] Building...")
        ctx.run("make")
        print("[jarvis][lcm][make] Installing...")
        ctx.run("make install")
        # Copy the lcm-gen binary into the Jarvis venv so it may be accessible
        # for other parts of the build process.
        print("[jarvis][lcm] Copying to jarvis venv...")
        shutil.copy("{}/bin/lcm-gen".format(ctx.product_env),
                    "{}/bin/lcm-gen".format(ctx.jarvis_env))

        # Install Python library
        print("[jarvis][lcm] Python installing...")
        with ctx.inside_product_env():
            with ctx.cd('lcm-python'):
                ctx.run("python setup.py install", hide='both')

    print("[jarvis][lcm] Installation complete")


def check_rapidjson(ctx):
    """
    Checks for the existence of RapidJson in the product venv.
    """
    return os.path.exists(ctx.get_product_file('include', 'rapidjson'))

def ensure_rapidjson(ctx):
    """
    Installs rapidjson into the product venv.
    """
    if check_rapidjson(ctx):
        print("[jarvis] rapidjson found in {}".format(ctx.product_env))
        return

    rapidjson_dir = os.path.join(ctx.third_party_root, 'rapidjson')
    ctx.ensure_product_env()
    with ctx.intermediate('rapidjson'):
        print("[jarvis] rapidjson not found in {}, installing".format(ctx.product_env))
        print("[jarvis][rapidjson] Retrieving source from {}".format(rapidjson_dir))
        ctx.run("cp -r \"{}\"/* .".format(rapidjson_dir))
        print("[jarvis][rapidjson][cmake] Generating buildsystem...")
        #ctx.run("mkdir -p build")
        #with ctx.cd("build"):
        ctx.run("cmake -DCMAKE_INSTALL_PREFIX={} .".format(
            ctx.product_env))
        print("[jarvis][rapidjson][cmake] Building and installing...")
        ctx.run("cmake --build . --target install")
        print("[jarvis][rapidjson] Installation complete")

def check_eigen(ctx):
    """
    Checks for the existance of Eigen in the product venv
    """
    return os.path.exists(ctx.get_product_file('include', 'eigen3'))

def ensure_eigen(ctx):
    """
    Installs eigen into the product venv.
    """    
    if check_eigen(ctx):
        print("[jarvis] eigen3 found in {}".format(ctx.product_env))
        return

    eigen_dir = os.path.join(ctx.third_party_root, 'eigen3')
    ctx.ensure_product_env()
    with ctx.intermediate('eigen3'):
        print("[jarvis] eigen3 not found in {}, installing".format(ctx.product_env))
        print("[jarvis][eigen3] Retrieving source from {}".format(eigen_dir))
        ctx.run("cp -r \"{}\"/* .".format(eigen_dir))
        ctx.run("mkdir -p build")
        with ctx.cd("build"):
            print("[jarvis][eigen3][cmake] Generating buildsystem...")
            ctx.run("cmake -DCMAKE_INSTALL_PREFIX={} ..".format(ctx.product_env))
            print("[jarvis][eigen3][cmake] Building and installing...")
            ctx.run("cmake --build . --target install")
            print("[jarvis][eigen3] Installation complete")
