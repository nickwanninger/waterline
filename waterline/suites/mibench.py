from waterline import Suite, Benchmark, Workspace
from waterline.utils import run_command
from pathlib import Path
import shutil


class MiBenchSimple(Benchmark):
    linker = "clang"
    linker_flags = []

    compiler = "gclang"
    source_files = []
    compile_flags = []

    def __init__(self, suite, name, source, **kwargs):
        super().__init__(suite, name)
        self.source = self.suite.src / source
        self.__dict__.update(kwargs)

    def compile(self, output: Path):
        print(f"compile {self.name}")
        self.shell(
            "sh",
            "-c",
            f"cd {self.source}; {self.compiler} -I. -lm -O1 {' '.join(self.compile_flags)} {' '.join(self.source_files)} -o {output}",
        )

    def link(self, object: Path, output: Path):
        self.shell(
            self.linker,
            "-lm",
            *self.linker_flags,
            object,
            "-o",
            output,
        )


class MiBenchMakefile(Benchmark):
    linker = "clang"
    linker_flags = []

    def __init__(self, suite, name, source, bin, **kwargs):
        super().__init__(suite, name)
        self.source = self.suite.src / source
        self.output_binary = bin
        self.__dict__.update(kwargs)

    def compile(self, output: Path):
        print(f"compile {self.name}")
        self.shell(
            "sh",
            "-c",
            f"cd {self.source}; make clean; CC=gclang CXX=gclang++ make",
        )
        shutil.copy(self.source / self.output_binary, output)

    def link(self, object: Path, output: Path):
        self.shell(
            self.linker,
            "-lm",
            *self.linker_flags,
            object,
            "-o",
            output,
        )


mibench_benchmarks = [
    # automotive/basicmath
    ("basicmath",),  # has patch
    # automotive/bincount
    ("bitcnts",),  # has patch
    # automotive/susan
    ("susan_s",),  # has patch
    ("susan_e",),  # has patch
    ("susan_c",),  # has patch
    # consumer/jpeg
    ("djpeg",),  # has patch
    ("cjpeg",),  # has patch
    # telecom/FFT
    ("fft",),  # has patch
    ("fft_inv",),  # has patch
    # telecom/CRC32
    # security/blowfish
    ("bf_d",),
    ("bf_e",),
    # office/stringsearch
    ("search",),
    ("rawdaudio",),
    ("rawcaudio",),
    ("untoast",),
    ("toast",),
    # working on:
    # done:
    ("sha",),  # security/sha
    ("crc",),  # telecomm/CRC32
    ("qsort",),  # automotive/qsort
]

toast_sources = [
    "src/add.c",
    "src/code.c",
    "src/debug.c",
    "src/decode.c",
    "src/long_term.c",
    "src/lpc.c",
    "src/preprocess.c",
    "src/rpe.c",
    "src/gsm_destroy.c",
    "src/gsm_decode.c",
    "src/gsm_encode.c",
    "src/gsm_explode.c",
    "src/gsm_implode.c",
    "src/gsm_create.c",
    "src/gsm_print.c",
    "src/gsm_option.c",
    "src/short_term.c",
    "src/table.c",
    "src/toast.c",
    "src/toast_lin.c",
    "src/toast_ulaw.c",
    "src/toast_alaw.c",
    "src/toast_audio.c",
]


jpeg_core = [
    "jmemnobs.c",
    "jcomapi.c",
    "jutils.c",
    "jerror.c",
    "jmemmgr.c",
    "jcapimin.c",
    "jcapistd.c",
    "jctrans.c",
    "jcparam.c",
    "jdatadst.c",
    "jcinit.c",
    "jcmaster.c",
    "jcmarker.c",
    "jcmainct.c",
    "jcprepct.c",
    "jccoefct.c",
    "jccolor.c",
    "jcsample.c",
    "jchuff.c",
    "jcphuff.c",
    "jcdctmgr.c",
    "jfdctfst.c",
    "jfdctflt.c",
    "jfdctint.c",
    "jdapimin.c",
    "jdapistd.c",
    "jdtrans.c",
    "jdatasrc.c",
    "jdmaster.c",
    "jdinput.c",
    "jdmarker.c",
    "jdhuff.c",
    "jdphuff.c",
    "jdmainct.c",
    "jdcoefct.c",
    "jdpostct.c",
    "jddctmgr.c",
    "jidctfst.c",
    "jidctflt.c",
    "jidctint.c",
    "jidctred.c",
    "jdsample.c",
    "jdcolor.c",
    "jquant1.c",
    "jquant2.c",
    "jdmerge.c",
]


class MiBench(Suite):
    name = "MiBench"

    def configure(self):
        # AUTOMOTIVE
        self.simple(
            "automotive/basicmath",
            "basicmath",
            source_files=["basicmath_large.c", "rad2deg.c", "cubic.c", "isqrt.c"],
        )

        self.simple(
            "automotive/bitcount",
            "bitcnts",
            source_files=[
                "bitcnt_1.c",
                "bitcnt_2.c",
                "bitcnt_3.c",
                "bitcnt_4.c",
                "bitcnts.c",
                "bitfiles.c",
                "bitstrng.c",
                "bstr_i.c",
            ],
        )

        self.simple(
            "automotive/qsort",
            "qsort",
            linker_flags=["-lm"],
            compile_flags=["-lm"],
            source_files=["qsort_large.c"],
        )
        self.simple("automotive/susan", "susan", source_files=["susan.c"])

        # CONSUMER
        # TODO: jpeg
        # TODO: lame
        # TODO: mad
        # TODO: tiff2bw
        # TODO: tiff2rgba
        # TODO: tiff-data
        # TODO: tiffdither
        # TODO: tiffmedian
        # TODO: tiff-v3.5.4
        # TODO: typeset
        self.simple(
            "consumer/jpeg/jpeg-6a",
            "cjpeg",
            source_files=[
                *jpeg_core,
                # sources for the app
                "cjpeg.c",
                "rdppm.c",
                "rdgif.c",
                "rdtarga.c",
                "rdrle.c",
                "rdbmp.c",
                "rdswitch.c",
                "cdjpeg.c",
            ],
        )
        # self.simple(
        #     "consumer/jpeg/jpeg-6a",
        #     "djpeg",
        #     source_files=[
        #         *jpeg_core,
        #         # sources for the app
        #         "djpeg.c",
        #         "wrppm.c",
        #         "wrgif.c",
        #         "wrtarga.c",
        #         "wrrle.c",
        #         "wrbmp.c",
        #         "rdcolmap.c",
        #         "cdjpeg.o",
        #     ],
        # )

        # NETWORK
        # TODO: patricia
        self.simple("network/dijkstra", "dijkstra", source_files=["dijkstra_large.c"])
        # self.simple(
        #     "network/patricia",
        #     "patricia",
        #     source_files=["patricia.c", "patricia_test.c"],
        # )

        # OFFICE
        # TODO: ghostscript
        # TODO: ispell
        # TODO: rsynth
        # TODO: sphinx
        self.simple(
            "office/stringsearch",
            "stringsearch",
            source_files=["bmhasrch.c", "bmhisrch.c", "bmhsrch.c", "pbmsrch_large.c"],
        )

        # SECURITY
        # TODO: pgp
        # TODO: rijndael (needs patched)
        self.simple(
            "security/blowfish",
            "bf",
            source_files=[
                "bf.c",
                "bf_skey.c",
                "bf_ecb.c",
                "bf_enc.c",
                "bf_cbc.c",
                "bf_cfb64.c",
                "bf_ofb64.c",
            ],
            compile_flags=["-fomit-frame-pointer"],
        )
        self.simple("security/sha", "sha", source_files=["sha_driver.c", "sha.c"])

        # TELECOMM
        self.simple(
            "telecomm/adpcm",
            "rawcaudio",
            compile_flags=["-Isrc/"],
            source_files=["src/rawcaudio.c", "src/adpcm.c"],
        )
        self.simple(
            "telecomm/adpcm",
            "rawdaudio",
            compile_flags=["-Isrc/"],
            source_files=["src/rawdaudio.c", "src/adpcm.c"],
        )
        self.simple(
            "telecomm/FFT", "fft", source_files=["main.c", "fftmisc.c", "fourierf.c"]
        )
        self.simple("telecomm/CRC32", "crc", source_files=["crc_32.c"])

        self.simple(
            "telecomm/gsm",
            "toast",
            compile_flags=[
                "-DSASR",
                "-DSTUPID_COMPILER",
                "-DNeedFunctionPrototypes=1",
                "-I./inc",
            ],
            source_files=toast_sources,
        )

        self.simple(
            "telecomm/gsm",
            "untoast",
            compile_flags=[
                "-DSASR",
                "-DSTUPID_COMPILER",
                "-DNeedFunctionPrototypes=1",
                "-I./inc",
            ],
            source_files=toast_sources,
        )

    def simple(self, dir, name, **kwargs):
        self.add_benchmark(MiBenchSimple, name, dir, **kwargs)

    def make(self, dir, name, outbin, **kwargs):
        self.add_benchmark(MiBenchMakefile, name, dir, outbin, **kwargs)

    def acquire(self):
        print("get mibench")
        self.workspace.shell(
            "git",
            "clone",
            "https://github.com/embecosm/mibench.git",
            self.src,
            "--depth",
            "1",
        )
