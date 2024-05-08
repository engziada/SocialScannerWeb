from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from apps.content_types import blueprint

from apps import db

from apps.content_types.forms import ContentForm
from apps.content_types.models import Content

from icecream import ic

from apps.home.models import Log
from apps.social.models import SocialAccount, SocialAccount_Content


@blueprint.route("/contents")
@login_required
def contents():
    """
    A route function that handles the '/contents' endpoint.

    This function is a route handler for the '/contents' endpoint. It is responsible for displaying a list of all contents in the database.

    Returns:
        A rendered template 'content/contents.html' with the contents data passed as a parameter.
    """
    contents = Content.query.all()  # Fetch all contents from the database
    return render_template("content/contents.html", contents=contents)


@blueprint.route("/content_add", methods=["GET", "POST"])
@login_required
@Log.add_log("إضافة محتوى")
def content_add():
    """
    A route function that handles the '/content_add' endpoint.

    This function is a route handler for the '/content_add' endpoint. It is responsible for adding a new content to the database.

    Returns:
        If the form is submitted and valid, it redirects to the 'content_add' route and flashes a success message.
        If the form is submitted but invalid, it renders the 'content/content_add.html' template with the form data.
        If the form is not submitted, it renders the 'content/content_add.html' template with an empty form.

    Raises:
        None
    """
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
@login_required
@Log.add_log("حذف محتوى")
def content_delete(content_id):
    """
    A route function that handles the '/content_delete/<int:content_id>' endpoint.

    This function is a route handler for the '/content_delete/<int:content_id>' endpoint. It is responsible for deleting a content from the database.

    Parameters:
        content_id (int): The ID of the content to be deleted.

    Returns:
        If the content is successfully deleted, it redirects to the 'content_blueprint.contents' route and flashes a success message.
        If the content does not exist, it redirects to the 'content_blueprint.contents' route and flashes an error message.

    Raises:
        None
    """
    content = Content.query.get(content_id)
    if not content:
        flash("المحتوى غير موجود", "danger")
        return redirect(url_for("content_blueprint.contents"))
    db.session.delete(content)
    db.session.commit()
    flash("تم حذف المحتوى", "success")
    return redirect(url_for("content_blueprint.contents"))


@blueprint.route("/content_edit/<int:content_id>", methods=["GET", "POST"])
@login_required
@Log.add_log("تعديل محتوى")
def content_edit(content_id):
    """
    A route function that handles the '/content_edit/<int:content_id>' endpoint.

    This function is a route handler for the '/content_edit/<int:content_id>' endpoint. It is responsible for editing a content in the database.

    Parameters:
        content_id (int): The ID of the content to be edited.

    Returns:
        If the content is successfully edited, it redirects to the 'content_blueprint.contents' route and flashes a success message.
        If the content does not exist, it redirects to the 'content_blueprint.contents' route and flashes an error message.
        If the form is submitted and valid, it updates the content in the database, commits the changes, and redirects to the 'content_blueprint.contents' route.
        If the form is submitted but invalid, it renders the 'content/content_edit.html' template with the form data.
        If the form is not submitted, it renders the 'content/content_edit.html' template with the content and social accounts.

    Raises:
        None
    """
    content = Content.query.get(content_id)
    if not content:
        flash("المحتوى غير موجود", "danger")
        return redirect(url_for("content_blueprint.contents"))
    
    socialaccounts = db.session.query(SocialAccount).\
        join(SocialAccount_Content).\
        join(Content).\
        filter(Content.id == content_id).\
        all()
            
    form = ContentForm(obj=content)  # Create an instance of the form
    if form.validate_on_submit():
                content.name = form.name.data
                content.description = form.description.data

                db.session.commit()
                flash("تم تعديل المحتوى", "success")
                return redirect(url_for("content_blueprint.contents"))
    
    return render_template(
        "content/content_edit.html", form=form, content=content, socialaccounts=socialaccounts)
