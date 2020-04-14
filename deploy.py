import paramiko
from os.path import expanduser
from user_definition import *


# ## Assumption : Anaconda, Git (configured)

def ssh_client():
    """Return ssh client object"""
    return paramiko.SSHClient()


def ssh_connection(ssh, ec2_address, user, key_file):
    """Connect to an SSH server and authenticate """
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ec2_address, username=user,
                key_filename=expanduser("~") + key_file)
    return ssh


def create_or_update_environment(ssh):
    """Create environment if non-existent,
    otherwise update the environment using the .yml file"""
    stdin, stdout, stderr = \
        ssh.exec_command("conda env create -f "
                         "~/" + git_repo_name + "/environment.yml")
    if (b'already exists' in stderr.read()):
        stdin, stdout, stderr = \
            ssh.exec_command("conda env update -f "
                             "~/" + git_repo_name + "/environment.yml")


def git_clone_first_repo(ssh):
    """Clone the first git repository"""
    stdin, stdout, stderr = ssh.exec_command("git --version")
    if (b"" is stderr.read()):
        git_clone_command = "git clone https://github.com/" + \
                            "willhaslett" + "/" + "covid-19-growth" + ".git"

        stdin, stdout, stderr = ssh.exec_command(git_clone_command)

        if (b'already exists' in stderr.read()):
            git_pull_command = "git -C /home/ec2-user/" \
                               + git_repo_name + " pull"
            stdin, stdout, stderr = ssh.exec_command(git_pull_command)

        cd_command = "cd covid-19-growth"
        stdin, stdout, stderr = ssh.exec_command(cd_command)
        venv_command = "cd covid-19-growth"
        stdin, stdout, stderr = ssh.exec_command(venv_command)
        activate_command = "source venv/bin/activate"
        stdin, stdout, stderr = ssh.exec_command(activate_command)
        pip_command = "pip install -q -r requirements.txt"
        stdin, stdout, stderr = ssh.exec_command(pip_command)
        # cd_up_command = "cd .."
        # stdin, stdout, stderr = ssh.exec_command(cd_up_command)


def git_clone(ssh):
    """Clone a git repository - defined in user_definition.py"""
    stdin, stdout, stderr = ssh.exec_command("git --version")
    if (b"" is stderr.read()):
        git_clone_command = "git clone https://github.com/" + \
                            git_user_id + "/" + git_repo_name + ".git"

        stdin, stdout, stderr = ssh.exec_command(git_clone_command)

        if (b'already exists' in stderr.read()):
            git_pull_command = "git -C /home/ec2-user/" \
                               + git_repo_name + " pull"
            stdin, stdout, stderr = ssh.exec_command(git_pull_command)


def pull_data(ssh):
    copy_usa_notebook_command = "cp /home/ec2-user/" + git_repo_name + "/code/notebooks/pull_USA_data.ipynb " +\
                                "/home/ec2-user/covid-19-growth/notebooks/pull_USA_data.ipynb"
    stdin, stdout, stderr = ssh.exec_command(copy_usa_notebook_command)
    copy_world_notebook_command = "cp /home/ec2-user/" + git_repo_name + "/code/notebooks/pull_world_data.ipynb " +\
                                "/home/ec2-user/covid-19-growth/notebooks/pull_world_data.ipynb"
    stdin, stdout, stderr = ssh.exec_command(copy_world_notebook_command)

    pull_usa_command = "jupyter nbconvert --execute " + \
                "/home/ec2-user/covid-19-growth/notebooks/pull_USA_data.ipynb"
    stdin, stdout, stderr = ssh.exec_command(pull_usa_command)

    pull_world_command = "jupyter nbconvert --execute " + \
               "/home/ec2-user/covid-19-growth/notebooks/pull_world_data.ipynb"
    stdin, stdout, stderr = ssh.exec_command(pull_world_command)


# def set_crontab(ssh):
#     """set a crontab to run google_search.py and event_brite.py every minute"""
#     stdin, stdout, stderr = ssh.exec_command("crontab -r")  # remove crontab
#
#     # pull usa data every hour
#     usa_cron = "* * * * * jupyter nbconvert --execute " + \
#         "/home/ec2-user/covid-19-growth/notebooks/pull_USA_data.ipynb"
#     # pull world data every hour
#     world_cron = "* * * * * jupyter nbconvert --execute " + \
#                "/home/ec2-user/covid-19-growth/notebooks/pull_world_data.ipynb"
#
#     cronline = usa_cron + '\n' + world_cron
#     stdin, stdout, stderr = ssh.exec_command("crontab -l | { cat; echo \""
#                                              + cronline + "\"; } | crontab -")


def run_app(ssh):
    """1. kill existing gunicorn processes
    2. make daemon bash script executable
    3. run app as daemon process
    4. print app's port number"""
    # kill all old gunicorns
    kill_command = 'pkill -f gunicorn'
    stdin, stdout, stderr = ssh.exec_command(kill_command)

    # make bash file executable
    make_executable = "chmod +x " + git_repo_name + "/run_daemon.sh"
    stdin, stdout, stderr = ssh.exec_command(make_executable)

    # run flask app as daemon (on port 8080)
    # execute = "gunicorn /home/ec2-user/covid-19/code/app:server -b :8080 &"
    execute = git_repo_name + "/run_daemon.sh"
    stdin, stdout, stderr = ssh.exec_command(execute)

    print(8080)  # app running on port 8080


def main():
    """Implement ssh protocol to connect remotely to amazon server"""
    ssh = ssh_client()
    ssh_connection(ssh, ec2_address, user, key_file)
    git_clone_first_repo(ssh)
    git_clone(ssh)
    pull_data(ssh)
    create_or_update_environment(ssh)
    # set_crontab(ssh)
    run_app(ssh)
    ssh.close()  # logout


if __name__ == '__main__':
    main()
