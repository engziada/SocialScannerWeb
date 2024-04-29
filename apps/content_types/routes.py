from flask import render_template, redirect, url_for, flash

from apps.content_types import blueprint

from apps import db

from apps.content_types.forms import ContentForm
from apps.content_types.models import Content

from icecream import ic

from apps.home.models import Log
from apps.social.models import SocialAccount, SocialAccount_Content


@blueprint.route("/contents")
# @login_required
def contents():
    contents = Content.query.all()  # Fetch all contents from the database
    return render_template("content/contents.html", contents=contents)


@blueprint.route("/content_add", methods=["GET", "POST"])
# @login_required
@Log.add_log("إضافة محتوى")
def content_add():
    form = ContentForm()  # Create an instance of the form
    if form.validate_on_submit():
        new_content = Content(
            name=form.name.data,
            description=form.description.data,
        )

        db.session.add(new_content)
        db.session.commit()
        flash("تم إضافة المحتوى", "success")

        return redirect(url_for("content_blueprint.content_add"))
    return render_template("content/content_add.html", form=form)


@blueprint.route("/content_delete/<int:content_id>", methods=["POST"])
# @login_required
@Log.add_log("حذف محتوى")
def content_delete(content_id):
    content = Content.query.get(content_id)
    if not content:
        flash("المحتوى غير موجود", "danger")
        return redirect(url_for("content_blueprint.contents"))
    db.session.delete(content)
    db.session.commit()
    flash("تم حذف المحتوى", "success")
    return redirect(url_for("content_blueprint.contents"))


@blueprint.route("/content_edit/<int:content_id>", methods=["GET", "POST"])
# @login_required
@Log.add_log("تعديل محتوى")
def content_edit(content_id):
    content = Content.query.get(content_id)
    if not content:
        flash("المحتوى غير موجود", "danger")
        return redirect(url_for("content_blueprint.contents"))
    
    socialaccounts = db.session.query(SocialAccount).\
        join(SocialAccount_Content).\
        join(Content).\
        filter(Content.id == content_id).\
        all()
        
    ic(socialaccounts)
    
    form = ContentForm(obj=content)  # Create an instance of the form
    if form.validate_on_submit():
                content.name = form.name.data
                content.description = form.description.data

                db.session.commit()
                flash("تم تعديل المحتوى", "success")
                return redirect(url_for("content_blueprint.contents"))
    
    return render_template(
        "content/content_edit.html", form=form, content=content, socialaccounts=socialaccounts)
