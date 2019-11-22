import sys
import unittest.mock

from install.tsg_install_info import install_info

# get inputs to test system I/O
try:
    from io import StringIO
except:
    from StringIO import StringIO


# class for testing subprocess.Popen()
class Test_Popen:
    def __init__(self, retval, noval, var):
        self.retval = retval
        self.noval = noval
        self.var = var
        self.use_retval = True
    def communicate(self):
        return [self]
    def decode(self, d):
        if (self.use_retval):  return self.retval
        else:                  return self.noval

    def id(self, args, stdout, stderr):
        return self
    def init_check_pkg_manager(self, args, stdout, stderr):
        if ((self.var == 'dpkg') and ('dpkg' in args)):
            self.use_retval = True
        elif ((self.var == 'rpm') and ('rpm' in args)):
            self.use_retval = True
        else:
            self.use_retval = False
        return self


# FILE: TSG_INSTALL.PY
from install import tsg_install

def test_get_install_error_codes():
    print("Testing get_install_error_codes()...", end='')
    # TODO: overwrite current file search, redirect to copy of file in testing
    install_err_codes = tsg_install.get_install_err_codes()
    assert(install_err_codes['NOT_DEFINED'] == "Because the necessary "\
        "dependencies are not installed, the auoms auditd plugin will not be "\
        "installed")
    assert(install_err_codes['2'] == "Invalid option provided to the shell "\
        "bundle; Run `sudo sh ./omsagent-*.universal*.sh --help` for usage")
    assert(install_err_codes['3'] == "No option provided to the shell bundle; "\
        "Run `sudo sh ./omsagent-*.universal*.sh --help` for usage")
    assert(install_err_codes['4'] == "Invalid package type OR invalid proxy "\
        "settings; omsagent-*rpm*.sh packages can only be installed on "\
        "RPM-based systems, and omsagent-*deb*.sh packages can only be "\
        "installed on Debian-based systems; We recommend that you use the "\
        "universal installer from the [latest release](https://github.com/"\
        "Microsoft/OMS-Agent-for-Linux/releases/latest). Also [review]"\
        "(https://github.com/Microsoft/OMS-Agent-for-Linux/blob/master/docs/"\
        "Troubleshooting.md#im-unable-to-connect-through-my-proxy-to-oms) your "\
        "proxy settings.")
    assert(install_err_codes['5'] == "The shell bundle must be executed as root "\
        "OR there was 403 error returned during onboarding; Run your command "\
        "using `sudo`")
    assert(install_err_codes['6'] == "Invalid package architecture OR there was "\
        "error 200 error returned during onboarding; omsagent-*x64.sh packages "\
        "can only be installed on 64-bit systems, and omsagent-*x86.sh packages "\
        "can only be installed on 32-bit systems; Download the correct package "\
        "for your architecture from the [latest release](https://github.com/"\
        "Microsoft/OMS-Agent-for-Linux/releases/latest)")
    assert(install_err_codes['17'] == "Installation of OMS package failed; Look "\
        "through the command output for the root failure")
    assert(install_err_codes['19'] == "Installation of OMI package failed; Look "\
        "through the command output for the root failure")
    assert(install_err_codes['20'] == "Installation of SCX package failed; Look "\
        "through the command output for the root failure")
    assert(install_err_codes['21'] == "Installation of Provider kits failed; "\
        "Look through the command output for the root failure")
    assert(install_err_codes['22'] == "Installation of bundled package failed; "\
        "Look through the command output for the root failure")
    assert(install_err_codes['23'] == "SCX or OMI package already installed; "\
        "Use `--upgrade` instead of `--install` to install the shell bundle")
    assert(install_err_codes['30'] == "Internal bundle error; File a [GitHub "\
        "Issue](https://github.com/Microsoft/OMS-Agent-for-Linux/issues) with "\
        "details from the output")
    assert(install_err_codes['55'] == "Unsupported openssl version OR Cannot "\
        "connect to Microsoft OMS service OR dpkg is locked OR Missing curl "\
        "program")
    assert(install_err_codes['61'] == "Missing Python ctypes library; Install "\
        "the Python ctypes library or package (python-ctypes)")
    assert(install_err_codes['62'] == "Missing tar program; Install tar")
    assert(install_err_codes['63'] == "Missing sed program; Install sed")
    assert(install_err_codes['64'] == "Missing curl program; Install curl")
    assert(install_err_codes['65'] == "Missing gpg program; Install gpg")
    print("Success!")

def test_ask_error_codes():
    print("Testing ask_error_codes()...", end='')
    # TODO: find way to mock different inputs? maybe mock variables instead
    # no installation error code
    with unittest.mock.patch.object(__builtins__, 'input', lambda x : 'n'):
        captured_output = StringIO()
        sys.stdout = captured_output
        result = tsg_install.ask_error_codes()
        sys.stdout = sys.__stdout__
        assert(result)
        assert(captured_output.getvalue() == "Continuing on with troubleshooter...\n")
    # installation error code, none
    def mocked_input_1(q):
        if (q == "Do you have an installation error code? (y/n): "):
            return 'y'
        elif (q == "Please input the error code: "):
            return 'none'
    with unittest.mock.patch.object(__builtins__, 'input', mocked_input_1):
        captured_output = StringIO()
        sys.stdout = captured_output
        result = tsg_install.ask_error_codes()
        sys.stdout = sys.__stdout__
        assert(result)
        assert(captured_output.getvalue() == "Continuing on with troubleshooter...\n")
    # installation error code, code, continue
    def mocked_input_2(q):
        if (q == "Do you have an installation error code? (y/n): "):
            return 'y'
        elif (q == "Please input the error code: "):
            return '62'
        elif (q == "Would you like to continue with the troubleshooter? (y/n): "):
            return 'y'
    with unittest.mock.patch.object(__builtins__, 'input', mocked_input_2):
        captured_output = StringIO()
        sys.stdout = captured_output
        result = tsg_install.ask_error_codes()
        sys.stdout = sys.__stdout__
        assert(result)
        assert(captured_output.getvalue() == "Error 62: Missing tar program; Install tar\n"\
               "Continuing on with troubleshooter...\n")
    # installation error code, code, don't continue
    def mocked_input_3(q):
        if (q == "Do you have an installation error code? (y/n): "):
            return 'y'
        elif (q == "Please input the error code: "):
            return '62'
        elif (q == "Would you like to continue with the troubleshooter? (y/n): "):
            return 'n'
    with unittest.mock.patch.object(__builtins__, 'input', mocked_input_3):
        captured_output = StringIO()
        sys.stdout = captured_output
        result = tsg_install.ask_error_codes()
        sys.stdout = sys.__stdout__
        assert(not result)
        assert(captured_output.getvalue() == "Error 62: Missing tar program; Install tar\n"\
               "Exiting troubleshooter...\n")
    print("Success!")

def test_check_pkg_manager():
    print("Testing check_pkg_manager()...", end="")
    # check dpkg
    dpkg_popen = Test_Popen('/usr/bin/dpkg', '', 'dpkg')
    with unittest.mock.patch('subprocess.Popen', dpkg_popen.init_check_pkg_manager):
        assert(tsg_install.check_pkg_manager())
        assert(install_info['INSTALLER'] == 'dpkg')
    # check rpm
    rpm_popen = Test_Popen('/usr/bin/rpm', '', 'rpm')
    with unittest.mock.patch('subprocess.Popen', rpm_popen.init_check_pkg_manager):
        assert(tsg_install.check_pkg_manager())
        assert(install_info['INSTALLER'] == 'rpm')
    # check neither
    neither_popen = Test_Popen('none', '', 'neither')
    with unittest.mock.patch('subprocess.Popen', neither_popen.init_check_pkg_manager):
        captured_output = StringIO()
        sys.stdout = captured_output
        result = tsg_install.check_pkg_manager()
        sys.stdout = sys.__stdout__
        assert(not result)
        assert(captured_output.getvalue() == "Error: this system does not have "\
               "a supported package manager. Please install 'dpkg' or 'rpm' and "\
               "run this troubleshooter again.\n")
    print("Success!")

def test_check_space():
    print("Testing check_space()...", end='')
    class Test_Statvfs:
        def __init__(self, f_bavail, f_frsize):
            self.f_bavail = f_bavail
            self.f_frsize = f_frsize
        def init_check_space(self, dirname):
            return self
    # enough space
    yes_space = Test_Statvfs(504289000, 10000)
    with unittest.mock.patch('os.statvfs', yes_space.init_check_space):
        assert(tsg_install.check_space())
    # not enough space
    no_space = Test_Statvfs(0, 0)
    with unittest.mock.patch('os.statvfs', no_space.init_check_space):
        captured_output = StringIO()
        sys.stdout = captured_output
        result = tsg_install.check_space()
        sys.stdout = sys.__stdout__
        assert(not result)
        assert(captured_output.getvalue() == "Error: directory /etc doesn't have "\
               "enough space to install OMS. Please free up some space and try "\
               "installing again.\nError: directory /opt doesn't have enough "\
               "space to install OMS. Please free up some space and try "\
               "installing again.\nError: directory /var doesn't have enough "\
               "space to install OMS. Please free up some space and try "\
               "installing again.\n")
    print("Success!")

def test_ask_reinstall():
    print("Testing ask_reinstall()...", end='')
    # yes to reinstall
    with unittest.mock.patch.object(__builtins__, 'input', lambda x : 'y'):
        captured_output = StringIO()
        sys.stdout = captured_output
        result = tsg_install.ask_reinstall()
        sys.stdout = sys.__stdout__
        assert(not result)
        assert(captured_output.getvalue() == "Please run the command `sudo sh "\
               "./omsagent-*.universal.x64.sh --purge` to uninstall, and `sudo "\
               "sh ./omsagent-*.universal.x64.sh --install` to reinstall.\n")
    # no to reinstall
    with unittest.mock.patch.object(__builtins__, 'input', lambda x : 'n'):
        captured_output = StringIO()
        sys.stdout = captured_output
        result = tsg_install.ask_reinstall()
        sys.stdout = sys.__stdout__
        assert(result)
        assert(captured_output.getvalue() == "Continuing on with troubleshooter...\n")
    print("Success!")

def test_check_cert():
    print("Testing check_cert()...", end='')
    # TODO: mock 'crt_path' to local file
    print("Success!")

def test_check_key():
    print("Testing check_key()...", end='')
    # TODO: mock 'key_path' to local file
    print("Success!")



# FILE: TSG_CHECKOS.PY
from install import tsg_checkos

def test_is_number():
    print("Testing is_number()...", end='')
    assert(tsg_checkos.is_number('321') == True)
    assert(tsg_checkos.is_number('3.4') == True)
    assert(tsg_checkos.is_number('bad') == False)
    assert(tsg_checkos.is_number('3f1') == False)
    assert(tsg_checkos.is_number('b44') == False)
    print("Success!")

def test_get_supported_versions():
    print("Testing get_supported_versions()...", end='')
    # TODO: change filepath to copy of file in testing
    tsg_checkos.get_supported_versions()
    # check supported_32bit
    assert(tsg_checkos.supported_32bit.keys() == {'centos','ol','rhel','debian',\
                                                'ubuntu'})
    assert(tsg_checkos.supported_32bit['centos'] == ['6'])
    assert(tsg_checkos.supported_32bit['ol']     == ['6'])
    assert(tsg_checkos.supported_32bit['rhel']   == ['6'])
    assert(tsg_checkos.supported_32bit['debian'] == ['8','9'])
    assert(tsg_checkos.supported_32bit['ubuntu'] == ['14.04','16.04'])
    # check supported_64bit
    assert(tsg_checkos.supported_64bit.keys() == {'centos','amzn','ol','rhel',\
                                                'debian','ubuntu','sles'})
    assert(tsg_checkos.supported_64bit['centos'] == ['6','7'])
    assert(tsg_checkos.supported_64bit['amzn']   == ['2017.09'])
    assert(tsg_checkos.supported_64bit['ol']     == ['6','7'])
    assert(tsg_checkos.supported_64bit['rhel']   == ['6','7'])
    assert(tsg_checkos.supported_64bit['debian'] == ['8','9'])
    assert(tsg_checkos.supported_64bit['ubuntu'] == ['14.04','16.04','18.04'])
    assert(tsg_checkos.supported_64bit['sles']   == ['12'])
    print("Success!")

def test_get_os_bits():
    print("Testing get_os_bits()...", end='')
    bit_test = Test_Popen("blah\n64-bit", '', '')
    with unittest.mock.patch('subprocess.Popen', bit_test.id):
        bits = tsg_checkos.get_os_bits()
        assert(bits == '64-bit')
        assert(install_info['CPU_BITS'] == '64-bit')
    print("Success!")

def test_get_os_version():
    print("Testing get_os_version()...", end='')
    # TODO: create own os file, use that to test
    tsg_checkos.get_os_version()
    # check install_info dictionary updated
    assert(install_info['OS_NAME'] == 'Ubuntu')
    assert(install_info['OS_VERSION'] == '18.04.3 LTS (Bionic Beaver)')
    assert(install_info['OS_ID'] == 'ubuntu')
    assert(install_info['OS_ID_LIKE'] == 'debian')
    assert(install_info['OS_PRETTY_NAME'] == 'Ubuntu 18.04.3 LTS')
    assert(install_info['OS_VERSION_ID'] == '18.04')
    assert(install_info['OS_HOME_URL'] == 'https://www.ubuntu.com/')
    assert(install_info['OS_SUPPORT_URL'] == 'https://help.ubuntu.com/')
    assert(install_info['OS_BUG_REPORT_URL'] == 'https://bugs.launchpad.net/'\
           'ubuntu/')
    assert(install_info['OS_PRIVACY_POLICY_URL'] == 'https://www.ubuntu.com/'\
           'legal/terms-and-policies/privacy-policy')
    assert(install_info['OS_VERSION_CODENAME'] == 'bionic')
    assert(install_info['OS_UBUNTU_CODENAME'] == 'bionic')
    print("Success!")

def test_print_wrong_version():
    print("Testing print_wrong_version()...", end='')
    # check for 32-bit, 1 supported version
    with unittest.mock.patch.dict(install_info, {'OS_NAME':'centos_name', \
        'OS_ID':'centos', 'OS_PRETTY_NAME':'centos_prettyname'}, clear=True):
        captured_output = StringIO()
        sys.stdout = captured_output
        tsg_checkos.print_wrong_version('32-bit')
        sys.stdout = sys.__stdout__
        assert(captured_output.getvalue() == "This version of centos_name "\
            "(centos_prettyname) is not supported. For 32-bit machines, please "\
            "download centos_name 6.\n")
    # check for 32-bit, 2+ supported versions
    with unittest.mock.patch.dict(install_info, {'OS_NAME':'ubuntu_name', \
        'OS_ID':'ubuntu', 'OS_PRETTY_NAME':'ubuntu_prettyname'}, clear=True):
        captured_output = StringIO()
        sys.stdout = captured_output
        tsg_checkos.print_wrong_version('32-bit')
        sys.stdout = sys.__stdout__
        assert(captured_output.getvalue() == "This version of ubuntu_name "\
            "(ubuntu_prettyname) is not supported. For 32-bit machines, please "\
            "download ubuntu_name 14.04 or 16.04.\n")
    # check for 64-bit, 1 supported version
    with unittest.mock.patch.dict(install_info, {'OS_NAME':'amazon_name', \
        'OS_ID':'amzn', 'OS_PRETTY_NAME':'amazon_prettyname'}, clear=True):
        captured_output = StringIO()
        sys.stdout = captured_output
        tsg_checkos.print_wrong_version('64-bit')
        sys.stdout = sys.__stdout__
        assert(captured_output.getvalue() == "This version of amazon_name "\
            "(amazon_prettyname) is not supported. For 64-bit machines, please "\
            "download amazon_name 2017.09.\n")
    # check for 64-bit, 2+ supported versions
    with unittest.mock.patch.dict(install_info, {'OS_NAME':'ubuntu_name', \
        'OS_ID':'ubuntu', 'OS_PRETTY_NAME':'ubuntu_prettyname'}, clear=True):
        captured_output = StringIO()
        sys.stdout = captured_output
        tsg_checkos.print_wrong_version('64-bit')
        sys.stdout = sys.__stdout__
        assert(captured_output.getvalue() == "This version of ubuntu_name "\
            "(ubuntu_prettyname) is not supported. For 64-bit machines, please "\
            "download ubuntu_name 14.04, 16.04 or 18.04.\n")
    print("Success!")

def test_check_os_version():
    print("Testing check_os_version()...", end='')
    # check for 32-bit success
    with unittest.mock.patch.dict(install_info, {'OS_ID':'ubuntu', \
            'OS_VERSION_ID':'14.04'}, clear=True):
        assert(tsg_checkos.check_os_version('32-bit'))
    # check for 64-bit success
    with unittest.mock.patch.dict(install_info, {'OS_ID':'ubuntu', \
            'OS_VERSION_ID':'18.04'}, clear=True):
        assert(tsg_checkos.check_os_version('64-bit'))
    # check for 32-bit wrong version
    with unittest.mock.patch.dict(install_info, {'OS_ID':'ubuntu', \
            'OS_VERSION_ID':'19.04'}, clear=True):
        captured_output = StringIO()
        sys.stdout = captured_output
        result = tsg_checkos.check_os_version('32-bit')
        sys.stdout = sys.__stdout__
        assert(not result)
        assert(captured_output.getvalue().startswith("This version of "))
    # check for 64-bit wrong version
        captured_output = StringIO()
        sys.stdout = captured_output
        result = tsg_checkos.check_os_version('64-bit')
        sys.stdout = sys.__stdout__
        assert(not result)
        assert(captured_output.getvalue().startswith("This version of "))
    # check for wrong OS
    with unittest.mock.patch.dict(install_info, {'OS_ID':'bad_id', \
        'OS_PRETTY_NAME':'bad_prettyname'}, clear=True):
        captured_output = StringIO()
        sys.stdout = captured_output
        result = tsg_checkos.check_os_version('64-bit')
        sys.stdout = sys.__stdout__
        assert(not result)
        assert(captured_output.getvalue() == "bad_prettyname is not supported.\n")
    print("Success!")

def test_check_os():
    print("Testing check_os()...", end='')
    # TODO: create good and bad OS files, test those
    assert(tsg_checkos.check_os())
    print("Sucess!")



# FILE: TSG_CHECKPKGS.PY
from install import tsg_checkpkgs

def test_get_dpkg_pkg_version():
    print("Testing get_dpkg_pkg_version()...", end='')
    # success

    # failure
    print("Success!")



# FILE: TSG_CHECKOMS.PY
from install import tsg_checkoms

def test_get_oms_version():
    print("Testing get_oms_version()...", end='')
    # TODO: change input? somehow get it more generic
    assert(tsg_checkoms.get_oms_version() == '1.12.7.0')
    print("Success!")

def test_get_curr_oms_version():
    print("Testing get_curr_oms_version()...", end='')
    # TODO: keep up to date with most recent published version
    assert(tsg_checkoms.get_curr_oms_version() == '1.12.7')
    print("Success!")

def test_comp_versions_ge():
    print("Testing comp_versions_ge()...", end='')
    assert(tsg_checkoms.comp_versions_ge('1.2', '1.1')   == True)
    assert(tsg_checkoms.comp_versions_ge('1.1', '1.12')  == False)
    assert(tsg_checkoms.comp_versions_ge('1.2.3', '1.1') == True)
    assert(tsg_checkoms.comp_versions_ge('1.2', '1.1.5') == True)
    assert(tsg_checkoms.comp_versions_ge('1.2.1', '1.3') == False)
    assert(tsg_checkoms.comp_versions_ge('1.2.0', '1.2') == True)
    assert(tsg_checkoms.comp_versions_ge('1.2', '1.2.0') == True)
    assert(tsg_checkoms.comp_versions_ge('1.2.x', '1.1') == True)
    assert(tsg_checkoms.comp_versions_ge('1.2', '1.2.x') == False)
    assert(tsg_checkoms.comp_versions_ge('1.2', '1.1r2') == True)
    assert(tsg_checkoms.comp_versions_ge('1.2', '1.3r2') == False)
    print("Success!")

def test_print_old_version():
    print("Testing print_old_version()...", end='')
    captured_output = StringIO()
    sys.stdout = captured_output
    tsg_checkoms.print_old_version('oms_version')
    sys.stdout = sys.__stdout__
    assert(captured_output == "You are currently running OMS Version "\
        "oms_version. This troubleshooter only supports versions 1.11 and "\
        "newer. Please head to the Github link below and click on 'Download "\
        "Latest OMS Agent for Linux (64-bit)' in order to update to the "\
        "newest version:\nhttps://github.com/microsoft/OMS-Agent-for-Linux\n"\
        "And follow the instructions given here:\nhttps://github.com/"\
        "microsoft/OMS-Agent-for-Linux/blob/master/docs/OMS-Agent-for-Linux.md"\
        "#upgrade-from-a-previous-release\n")
    print("Success!")

def test_ask_update_old_version():
    print("Testing ask_update_old_version()...", end='')
    with unittest.mock.patch.object(__builtins__, 'input', lambda: 'n'):
        captured_output = StringIO()
        sys.stdout = captured_output
        result = tsg_checkoms.ask_update_old_version('oms_version', 'curr_version')
        sys.stdout = sys.__stdout__
        assert(result)
        assert(captured_output == "You are currently running OMS Version "\
            "oms_version. There is a newer version available which may fix your "\
            "issue (version curr_version).\nContinuing on with troubleshooter...\n")
    with unittest.mock.patch.object(__builtins__, 'input', lambda: 'y'):
        captured_output = StringIO()
        sys.stdout = captured_output
        result = tsg_checkoms.ask_update_old_version('oms_version', 'curr_version')
        sys.stdout = sys.__stdout__
        assert(not result)
        assert(captured_output == "You are currently running OMS Version "\
            "oms_version. There is a newer version available which may fix your "\
            "issue (version curr_version).\nPlease head to the Github link below "\
            "and click on 'Download Latest OMS Agent for Linux (64-bit)' in "\
            "order to update to the newest version:\nhttps://github.com/microsoft/"\
            "OMS-Agent-for-Linux\nAnd follow the instructions given here:\n"\
            "https://github.com/microsoft/OMS-Agent-for-Linux/blob/master/docs/"\
            "OMS-Agent-for-Linux.md#upgrade-from-a-previous-release\n")
    print("Success!")

def test_update_install_info():
    print("Testing update_install_info()...", end='')
    # TODO: change filepath to own generic file
    assert(tsg_checkoms.update_install_info())
    assert(install_info['WORKSPACE_ID'] == 'f477ebdd-35ce-4366-8c2c-30692d040258')
    assert(install_info['AGENT_GUID'] == '5ae93bcf-4cca-4d73-8aaa-6706b78a8550')
    assert(install_info['LOG_FACILITY'] == 'local0')
    assert(install_info['CERTIFICATE_UPDATE_ENDPOINT'] == 'https://f477ebdd-35ce'\
        '-4366-8c2c-30692d040258.oms.opinsights.azure.com/ConfigurationService.Svc/'\
        'RenewCertificate')
    assert(install_info['URL_TLD'] == 'opinsights.azure.com')
    assert(install_info['DSC_ENDPOINT'] == "https://wus2-agentservice-prod-1."\
        "azure-automation.net/Accounts/f477ebdd-35ce-4366-8c2c-30692d040258/"\
        "Nodes\(AgentId='5ae93bcf-4cca-4d73-8aaa-6706b78a8550'\)")
    assert(install_info['OMS_ENDPOINT'] == 'https://f477ebdd-35ce-4366-8c2c-'\
        '30692d040258.ods.opinsights.azure.com/OperationalData.svc/PostJsonDataItems')
    assert(install_info['AZURE_RESOURCE_ID'] == '/subscriptions/13723929-6644-'\
        '4060-a50a-cc38ebc5e8b1/resourceGroups/aswatt-test/providers/Microsoft.'\
        'Compute/virtualMachines/aswatt-vm-test')
    assert(install_info['OMS_CLOUD_ID'] == '7783-7084-3265-9085-8269-3286-77')
    assert(install_info['UUID'] == 'B7785DED-E5AE-C244-A0E0-7FE31DEDD4ED')
    print("Success!")

def test_check_oms():
    print("Testing check_oms()...", end='')
    # TODO: change filepath?? idk figure out a way to test negative
    assert(tsg_checkoms.check_oms())
    print("Success!")


    




def test_all():
    print("TESTING TSG_INSTALL.PY...")
    test_get_install_error_codes()
    test_ask_error_codes()
    test_check_pkg_manager()
    test_check_space()
    test_ask_reinstall()
    test_check_cert()
    test_check_key()
    print("ALL TESTS PASSED FOR TSG_INSTALL.PY!\n")

    print("TESTING TSG_CHECKOS.PY...")
    test_is_number()
    test_get_supported_versions()
    test_get_os_bits()
    test_get_os_version()
    test_print_wrong_version()
    test_check_os_version()
    test_check_os()
    print("ALL TESTS PASSED FOR TSG_CHECKOS.PY!\n")

    print("TESTING TSG_CHECKOMS.PY...")
    test_get_oms_version()
    test_get_curr_oms_version()
    test_comp_versions_ge()
    test_print_old_version()
    test_ask_update_old_version()
    test_update_install_info()
    test_check_oms()
    print("ALL TESTS PASSED FOR TSG_CHECKOMS.PY!\n")

test_all()