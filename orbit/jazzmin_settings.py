# Jazzmin admin theme configuration

JAZZMIN_SETTINGS = {
    "site_title": "Orbit Admin",
    "site_header": "Orbit",
    "site_brand": "Orbit",
    "site_logo": None,
    "login_logo": None,
    "welcome_sign": "Welcome to Orbit",
    "copyright": "Bunnyland",
    "search_model": ["orbit.Person", "orbit.Conversation"],
    "user_avatar": None,
    
    # Top Menu
    "topmenu_links": [
        {"name": "Home", "url": "frontend"},
        {"name": "Admin", "url": "admin:index", "permissions": ["auth.view_user"]},
    ],

    # User Menu on the right side of the header
    "usermenu_links": [],

    # Side Menu
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["orbit", "orbit.person", "orbit.conversation", "auth", "auth.user"],

    # Custom CSS/JS
    "custom_css": None,
    "custom_js": None,
    
    # Icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "orbit.Person": "fas fa-user-friends",
        "orbit.Conversation": "fas fa-comments",
        "orbit.ContactAttempt": "fas fa-phone",
        "orbit.Relationship": "fas fa-heart",
    },

    # UI Tweaks
    "related_modal_active": False,
    "custom_links": {},
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-primary navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
}