def alumni_status_context(request):
    """
    Passes the alumni status variables from the middleware
    into the template context.
    """
    return {
        'is_alumni_approved': getattr(request, 'is_alumni_approved', False),
        'has_filled_tracer': getattr(request, 'has_filled_tracer', False)
    }