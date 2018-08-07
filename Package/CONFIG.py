import ops
import iopc

TARBALL_FILE="harfbuzz-1.7.6.tar.bz2"
TARBALL_DIR="harfbuzz-1.7.6"
INSTALL_DIR="harfbuzz-bin"
pkg_path = ""
output_dir = ""
tarball_pkg = ""
tarball_dir = ""
install_dir = ""
install_tmp_dir = ""
cc_host = ""
tmp_include_dir = ""
dst_include_dir = ""
dst_lib_dir = ""

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global install_tmp_dir
    global tarball_dir
    global cc_host
    global tmp_include_dir
    global dst_include_dir
    global dst_lib_dir
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    install_tmp_dir = ops.path_join(output_dir, INSTALL_DIR + "-tmp")
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    cc_host_str = ops.getEnv("CROSS_COMPILE")
    cc_host = cc_host_str[:len(cc_host_str) - 1]
    tmp_include_dir = ops.path_join(output_dir, ops.path_join("include",args["pkg_name"]))
    dst_include_dir = ops.path_join("include",args["pkg_name"])
    dst_lib_dir = ops.path_join(install_dir, "lib")

def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    ops.exportEnv(ops.setEnv("CXX", ops.getEnv("CROSS_COMPILE") + "g++"))
    ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    ops.exportEnv(ops.setEnv("DESTDIR", install_tmp_dir))
    #ops.exportEnv(ops.setEnv("PKG_CONFIG_LIBDIR", ops.path_join(iopc.getSdkPath(), "pkgconfig")))
    #ops.exportEnv(ops.setEnv("PKG_CONFIG_SYSROOT_DIR", iopc.getSdkPath()))

    cc_sysroot = ops.getEnv("CC_SYSROOT")
    cflags = ""
    cflags += " -I" + ops.path_join(cc_sysroot, 'usr/include')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libz')

    ldflags = ""
    ldflags += " -L" + ops.path_join(cc_sysroot, 'lib')
    ldflags += " -L" + ops.path_join(cc_sysroot, 'usr/lib')
    ldflags += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')

    libs = ""
    libs += " -lz "
    #ops.exportEnv(ops.setEnv("LDFLAGS", ldflags))
    #ops.exportEnv(ops.setEnv("CFLAGS", cflags))
    #ops.exportEnv(ops.setEnv("LIBS", libs))

    return False

def MAIN_EXTRACT(args):
    set_global(args)

    ops.unTarBz2(tarball_pkg, output_dir)
    ops.copyto(ops.path_join(iopc.getSdkPath(), 'usr/include/libz/.'), tarball_dir)
    #ops.copyto(ops.path_join(pkg_path, "finit.conf"), output_dir)

    return True

def MAIN_PATCH(args, patch_group_name):
    set_global(args)
    for patch in iopc.get_patch_list(pkg_path, patch_group_name):
        if iopc.apply_patch(tarball_dir, patch):
            continue
        else:
            sys.exit(1)

    return True

def MAIN_CONFIGURE(args):
    set_global(args)

    extra_conf = []
    extra_conf.append("--host=" + cc_host)
    extra_conf.append("V=1")
    cflags = ""
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libglib/glib-2.0')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libglib')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libpcre3')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/freetype')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/freetype/freetype2')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/fontconfig')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/fontconfig/fontconfig')

    libs = ""
    libs += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')
    libs += " -lglib-2.0 -lpcre"
    libs += " -lfreetype"
    libs += " -lfontconfig -luuid"
    extra_conf.append("GLIB_CFLAGS=" + cflags)
    extra_conf.append("GLIB_LIBS=" + libs)
    extra_conf.append("FREETYPE_CFLAGS=" + cflags)
    extra_conf.append("FREETYPE_LIBS=" + libs)
    extra_conf.append("FONTCONFIG_CFLAGS=" + cflags)
    extra_conf.append("FONTCONFIG_LIBS=" + libs)

    iopc.configure(tarball_dir, extra_conf)

    return True

def MAIN_BUILD(args):
    set_global(args)

    ops.mkdir(install_dir)
    ops.mkdir(install_tmp_dir)
    iopc.make(tarball_dir)
    iopc.make_install(tarball_dir)

    ops.mkdir(install_dir)
    ops.mkdir(dst_lib_dir)
    libharfbuzz_subset = "libharfbuzz-subset.so.0.10706.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libharfbuzz_subset), dst_lib_dir)
    ops.ln(dst_lib_dir, libharfbuzz_subset, "libharfbuzz-subset.so.0.10706")
    ops.ln(dst_lib_dir, libharfbuzz_subset, "libharfbuzz-subset.so.0")
    ops.ln(dst_lib_dir, libharfbuzz_subset, "libharfbuzz-subset.so")

    libharfbuzz = "libharfbuzz.so.0.10706.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libharfbuzz), dst_lib_dir)
    ops.ln(dst_lib_dir, libharfbuzz, "libharfbuzz.so.0.10706")
    ops.ln(dst_lib_dir, libharfbuzz, "libharfbuzz.so.0")
    ops.ln(dst_lib_dir, libharfbuzz, "libharfbuzz.so")

    libharfbuzz_icu = "libharfbuzz-icu.so.0.10706.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libharfbuzz_icu), dst_lib_dir)
    ops.ln(dst_lib_dir, libharfbuzz_icu, "libharfbuzz-icu.so.0.10706")
    ops.ln(dst_lib_dir, libharfbuzz_icu, "libharfbuzz-icu.so.0")
    ops.ln(dst_lib_dir, libharfbuzz_icu, "libharfbuzz-icu.so")

    ops.mkdir(tmp_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/."), tmp_include_dir)
    return False

def MAIN_INSTALL(args):
    set_global(args)

    iopc.installBin(args["pkg_name"], ops.path_join(ops.path_join(install_dir, "lib"), "."), "lib")
    iopc.installBin(args["pkg_name"], ops.path_join(tmp_include_dir, "."), dst_include_dir)

    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

