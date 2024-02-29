run:
	python manage.py migrate
	python manage.py runserver 0.0.0.0:8000

work:
	python manage.py rqworker

sync:
	rsync -rav morningcreative:/mnt/volume_lon1_15/* .
	python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.get(); u.set_password('stevenpage1970'); u.save()"
