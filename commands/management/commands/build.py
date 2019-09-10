from django.core.management.base import BaseCommand
import sys
import subprocess as sp

class Command(BaseCommand):
    help = 'Builds the Docker image of the project.'

    @staticmethod
    def print_fail(message, end = '\n'):
        sys.stderr.write('\x1b[1;31m' + message.strip() + '\x1b[0m' + end)

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            nargs='?',
            type=str,
            default='./Dockerfile',
            help='Path of Dockerfile'
        )
        parser.add_argument(
            '-t',
            '--tag',
            nargs='?',
            type=str,
            default='hs-api',
            help='Tag/Name of docker image'
        )
        parser.add_argument(
            '--push',
            action='store_true',
            help='Push to docker repository after build.'
        )
        parser.add_argument(
            '--prod',
            action='store_true',
            help='Build production image.'
        )
        parser.add_argument(
            '--run',
            action='store_true',
            help='Run image after build.'
        )

    def container_tag_exists(self, tag):
        tags = str(sp.check_output(["docker ps -a --format '{{.Names}}'"], shell=True)
            .decode('utf-8')).split("\n")
        return tag in tags
    
    def container_port_occupied(self):
        ports = str(sp.check_output(["docker ps -a --format '{{.Ports}}'"], shell=True)
            .decode('utf-8')).split("\n")
        return "0.0.0.0:8000->8000/tcp" in ports
    
    def export_container_env(self, tag, env_file):
        # TODO: find a better way to do this
        command = f"docker exec -it {tag} "
        try:
            env_file = open(env_file)
            env_var = env_file.readline()
            while env_var:
                sp.Popen([command + f"export {env_var}"], shell=True).wait()
        except:
            self.print_fail("Unable to open environment file")
            
    def _run_image(self, tag):
        """
        Runs the built docker image
        """
        # TODO: Add port and tag arguments
        if self.container_tag_exists(tag + "_exec"):
            self.print_fail("Tag already exists. Overriding existing container.")
            sp.Popen([f"docker stop {tag}"], shell=True).wait()
            sp.Popen([f"docker rm {tag}"], shell=True).wait()
        if self.container_port_occupied():
            self.print_fail("Port 8000>tcp already in use. Unable to run image.")
        else:
            sp.Popen(["docker run --name " + tag + "_exec -tid -p 8000:8000 " + tag], shell=True).wait()


    def _build_image(self, tag, file_path):
        """
        Builds the docker image using file and tag
        """
        # TODO: Add monitoring and exception handling
        sp.Popen(["docker build" + " -t " + tag + " . -f " + file_path], shell=True).wait()


    def _push_image(self, tag):
        """
        Push image to docker repository
        """
        # TODO: Add support for third party docker repositories and login exceptions
        info = str(sp.check_output(["docker info"], shell=True)
            .decode('utf-8')).split("\n")
        info = list(filter(lambda a: "Username" in a, info))
        try:
            username = info[0].split(":")[1][1:]
            if username:
                if len(tag.split("/")) == 1:
                    sp.Popen(["docker tag " + tag + f' {username}/{tag}'], shell=True).wait()
                    sp.Popen(["docker rmi " + tag], shell=True).wait()
                    tag = f'{username}/{tag}'
            else:
                self.print_fail("Not logged into docker.io. Please login and try again.")
                return
        except:
            self.print_fail("Unable to detect username. Pushing regardless...")
        sp.Popen([f'docker push docker.io/{tag}'], shell=True).wait()
        

    def handle(self, *args, **kwargs):
        prod = kwargs.get('prod', False)
        file_path = kwargs.get('file', './Dockerfile')
        tag = kwargs.get('tag', "hs-api")
        push = kwargs.get('push', False)
        run = kwargs.get('run', True)
        step = 1
        if (not prod) and file_path == './Dockerfile':
            file_path += ".dev"
        print(f'\n{str(step)}: Building {tag} with {file_path}...')
        step += 1
        self._build_image(tag, file_path)
        if run:
            print(f'\n{str(step)}: Running {tag} image...')
            self._run_image(tag)
            step += 1
        if push:
            print(f'\n{str(step)}: Pushing {tag} to docker repository...')
            self._push_image(tag)
            step += 1

