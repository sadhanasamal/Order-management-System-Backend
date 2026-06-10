from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError


@transaction.atomic
def scd2_update(*, model, record_id, build_create_kwargs, created_by, record_label='Record'):
    """
    Generic SCD Type 2 update for any Django model.

    The model must have: is_active, is_deleted, created_by, created_at fields.

    build_create_kwargs: callable that receives the old record and returns a dict
                         of field values for the new record.
    """
    try:
        old_record = model.objects.select_for_update().get(id=record_id, is_deleted=False, is_active=True)
    except model.DoesNotExist:
        raise ValidationError(f"{record_label} with id {record_id} not found or is inactive.")

    create_kwargs = build_create_kwargs(old_record)

    old_record.is_active = False
    old_record.save()

    try:
        new_record = model.objects.create(
            **create_kwargs,
            is_active=True,
            created_by=created_by,
        )
    except IntegrityError as e:
        raise ValidationError(f"Failed to create new {record_label} record: {str(e)}")

    return new_record


@transaction.atomic
def scd2_soft_delete(*, model, record_id, record_label='Record'):
    """
    Generic soft delete for any Django model with is_deleted and is_active fields.
    """
    try:
        record = model.objects.select_for_update().get(id=record_id, is_deleted=False, is_active=True)
    except model.DoesNotExist:
        raise ValidationError(f"{record_label} with id {record_id} not found or already deleted.")

    record.is_active = False
    record.is_deleted = True
    record.save()

    return record
