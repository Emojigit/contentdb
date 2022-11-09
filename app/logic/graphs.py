import datetime
from datetime import timedelta
from app.models import User, Package, PackageDailyStats, db, PackageState
from sqlalchemy import func


def daterange(start_date, end_date):
	for n in range(int((end_date - start_date).days) + 1):
		yield start_date + timedelta(n)


keys = ["platform_minetest", "platform_other", "reason_new",
		"reason_dependency", "reason_update"]


def _flatten_data(stats):
	if len(stats) == 0:
		return None

	start_date = stats[0].date
	end_date = stats[-1].date
	result = {
		"start": start_date.isoformat(),
		"end": end_date.isoformat(),
	}

	for key in keys:
		result[key] = []

	i = 0
	for date in daterange(start_date, end_date):
		stat = stats[i]
		if stat.date == date:
			for key in keys:
				result[key].append(getattr(stat, key))

			i += 1
		else:
			for key in keys:
				result[key].append(0)

	return result


def get_package_stats(package: Package):
	stats = package.daily_stats.order_by(db.asc(PackageDailyStats.date)).all()
	return _flatten_data(stats)


def get_package_stats_for_user(user: User):
	stats = db.session \
		.query(PackageDailyStats.date,
			func.sum(PackageDailyStats.platform_minetest).label("platform_minetest"),
			func.sum(PackageDailyStats.platform_other).label("platform_other"),
			func.sum(PackageDailyStats.reason_new).label("reason_new"),
			func.sum(PackageDailyStats.reason_dependency).label("reason_dependency"),
			func.sum(PackageDailyStats.reason_update).label("reason_update")) \
		.filter(PackageDailyStats.package.has(author_id=user.id)) \
		.order_by(db.asc(PackageDailyStats.date)) \
		.group_by(PackageDailyStats.date) \
		.all()

	results = _flatten_data(stats)
	results["package_downloads"] = get_package_overview_for_user(user, stats[0].date, stats[-1].date)

	return results


def get_package_overview_for_user(user: User, start_date: datetime.date, end_date: datetime.date):
	stats = db.session \
		.query(PackageDailyStats.package_id, PackageDailyStats.date,
			(PackageDailyStats.platform_minetest + PackageDailyStats.platform_other).label("downloads")) \
		.filter(PackageDailyStats.package.has(author_id=user.id, state=PackageState.APPROVED)) \
		.order_by(db.asc(PackageDailyStats.package_id), db.asc(PackageDailyStats.date)) \
		.all()

	stats_by_package = {}
	for stat in stats:
		bucket = stats_by_package.get(stat.package_id, [])
		stats_by_package[stat.package_id] = bucket

		bucket.append(stat)

	package_title_by_id = {}
	for package in user.packages.filter_by(state=PackageState.APPROVED).all():
		package_title_by_id[package.id] = package.title

	result = {}

	for package_id, stats in stats_by_package.items():
		i = 0
		row = []
		result[package_title_by_id[package_id]] = row
		for date in daterange(start_date, end_date):
			if i >= len(stats):
				row.append(0)
				continue

			stat = stats[i]
			if stat.date == date:
				row.append(stat.downloads)
				i += 1
			else:
				row.append(0)


	return result
