from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask

ALL_TASKS = [
    'remove_expired_otps',
]


# TODO: print with color
class Command(BaseCommand):
    help = 'Runs tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '-t',
            '--tasks',
            nargs='+',
            type=str,
            default=ALL_TASKS,
            help='Run only the specified tasks'
        )
        parser.add_argument(
            '-e',
            '--exclude-tasks',
            nargs='+',
            type=str,
            default=[],
            help='Exclude the specified tasks'
        )
        parser.add_argument(
            '-o',
            '--override-tasks',
            nargs='+',
            type=str,
            default=['__all__'],
            help='Override "script level" changes in specified tasks.'
                 '`__all__` will override all tasks.'
        )
        parser.add_argument(
            '-l',
            '--list',
            action='store_true',
            help='List known tasks'
        )

    def _remove_expired_otps(self, task_name, override_existing_task=False):
        """Delete expired tokens "Every week 6 AM" = "0 6 */7 * *"
        """
        task = 'apps.user.tasks.remove_expired_otps'
        crontab_config = {
            'minute': '0',
            'hour': '6',
            'day_of_week': '*/7',
            'day_of_month': '*',
            'month_of_year': '*'
        }

        periodic_task, _ = PeriodicTask.objects.get_or_create(
            name=f'{task_name}'
        )

        if override_existing_task:
            schedule, _ = CrontabSchedule.objects.get_or_create(
                **crontab_config)
            periodic_task.crontab = schedule
            periodic_task.task = task
            periodic_task.save()

        return periodic_task

    def _show_tasks(self):
        """Shows all known tasks using `ALL_TASKS` list
        """
        print('Tasks:')
        for idx, task in enumerate(ALL_TASKS):
            print(f'{idx + 1}. {task}')
        print()

    def _disable_task(self, task):
        task.enabled = False
        task.save()

    def _setup_tasks(self, tasks, exclude_tasks, override_tasks):
        """Get/create a periodic task.
        Disable it, if specified in `exclude_tasks`
        Override it, if specified in `override_tasks`"""
        enabled_tasks = []
        for task in tasks:
            # call function if exists
            override_existing_task = (
                '__all__' in override_tasks or
                task in override_tasks
            )
            periodic_task = getattr(
                self,
                f'_{task}',
                lambda: None
            )(task, override_existing_task=override_existing_task)
            if task in exclude_tasks:
                self._disable_task(periodic_task)
            else:
                enabled_tasks.append({
                    'task_name': task,
                    'task_id': periodic_task.id,
                    'task_crontab': str(periodic_task.crontab)
                })

        print("Enabled Tasks:")
        for task in enabled_tasks:
            task_name = task['task_name']
            task_id = task['task_id']
            task_crontab = task['task_crontab']

            print(f"Task #{task_id}: {task_name} - {task_crontab}")
        print()

    def handle(self, *args, **kwargs):
        if kwargs.get('list', False):
            self._show_tasks()
        else:
            tasks = kwargs.get('tasks', ALL_TASKS)
            exclude_tasks = kwargs.get('exclude_tasks', [])
            override_tasks = kwargs.get('override_tasks', [])
            self._setup_tasks(tasks, exclude_tasks, override_tasks)
