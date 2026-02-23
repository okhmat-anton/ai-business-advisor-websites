"""
Block template library data.
These are the predefined block templates users can add to their pages.
"""

BLOCK_TEMPLATES = [
    # Cover blocks
    {
        "type": "CoverBlock01",
        "category": "cover",
        "name": "Cover with centered text",
        "description": "Full-width cover with centered heading, subheading, and CTA button",
        "thumbnail": "",
        "defaultContent": {
            "title": "Welcome to Our Website",
            "subtitle": "We create amazing digital experiences",
            "buttonText": "Learn More",
            "buttonUrl": "#",
            "backgroundImage": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920",
            "overlayOpacity": 0.5,
        },
        "defaultSettings": {
            "paddingTop": "0px",
            "paddingBottom": "0px",
            "backgroundColor": "#1a1a2e",
            "align": "center",
            "fullWidth": True,
        },
        "htmlTemplate": "",
    },
    {
        "type": "CoverBlock02",
        "category": "cover",
        "name": "Cover with left-aligned text",
        "description": "Cover with text on the left side and image background",
        "thumbnail": "",
        "defaultContent": {
            "title": "Build Something Great",
            "subtitle": "Start your journey with us today",
            "buttonText": "Get Started",
            "buttonUrl": "#",
            "backgroundImage": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1920",
            "overlayOpacity": 0.6,
        },
        "defaultSettings": {
            "paddingTop": "0px",
            "paddingBottom": "0px",
            "backgroundColor": "#0f3460",
            "align": "left",
            "fullWidth": True,
        },
        "htmlTemplate": "",
    },
    {
        "type": "CoverBlock03",
        "category": "cover",
        "name": "Cover with video background",
        "description": "Full-screen cover with video background placeholder",
        "thumbnail": "",
        "defaultContent": {
            "title": "Innovation Starts Here",
            "subtitle": "Transforming ideas into reality",
            "buttonText": "Watch Video",
            "buttonUrl": "#",
            "backgroundImage": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1920",
            "overlayOpacity": 0.4,
        },
        "defaultSettings": {
            "paddingTop": "0px",
            "paddingBottom": "0px",
            "backgroundColor": "#16213e",
            "align": "center",
            "fullWidth": True,
        },
        "htmlTemplate": "",
    },
    # About blocks
    {
        "type": "AboutBlock01",
        "category": "about",
        "name": "About with image on the right",
        "description": "Text on left, image on right",
        "thumbnail": "",
        "defaultContent": {
            "title": "About Our Company",
            "text": "We are a team of dedicated professionals committed to delivering exceptional results.",
            "image": "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=800",
        },
        "defaultSettings": {
            "paddingTop": "80px",
            "paddingBottom": "80px",
            "backgroundColor": "#ffffff",
            "align": "left",
        },
        "htmlTemplate": "",
    },
    {
        "type": "AboutBlock02",
        "category": "about",
        "name": "About with counters",
        "description": "Description text with stat counters",
        "thumbnail": "",
        "defaultContent": {
            "title": "What We Do",
            "text": "Our mission is to help businesses grow through innovative technology solutions.",
            "counters": [
                {"value": "150+", "label": "Projects Done"},
                {"value": "50+", "label": "Happy Clients"},
                {"value": "10+", "label": "Years Experience"},
                {"value": "25", "label": "Team Members"},
            ],
        },
        "defaultSettings": {
            "paddingTop": "80px",
            "paddingBottom": "80px",
            "backgroundColor": "#f8f9fa",
            "align": "center",
        },
        "htmlTemplate": "",
    },
    # Text blocks
    {
        "type": "TextBlock01",
        "category": "text",
        "name": "Simple text block",
        "description": "Basic text block with title and paragraph",
        "thumbnail": "",
        "defaultContent": {
            "title": "Section Title",
            "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        },
        "defaultSettings": {
            "paddingTop": "60px",
            "paddingBottom": "60px",
            "backgroundColor": "#ffffff",
            "align": "center",
        },
        "htmlTemplate": "",
    },
    {
        "type": "TextBlock02",
        "category": "text",
        "name": "Two-column text",
        "description": "Text split into two columns",
        "thumbnail": "",
        "defaultContent": {
            "title": "Our Approach",
            "leftText": "We believe in a methodical approach to solving complex problems.",
            "rightText": "With cutting-edge tools and proven methodologies, we deliver solutions.",
        },
        "defaultSettings": {
            "paddingTop": "60px",
            "paddingBottom": "60px",
            "backgroundColor": "#ffffff",
            "align": "left",
        },
        "htmlTemplate": "",
    },
    # Heading block
    {
        "type": "HeadingBlock01",
        "category": "heading",
        "name": "Section heading",
        "description": "Large heading with optional subtitle",
        "thumbnail": "",
        "defaultContent": {
            "title": "Section Heading",
            "subtitle": "Optional subtitle text goes here",
            "level": "h2",
        },
        "defaultSettings": {
            "paddingTop": "40px",
            "paddingBottom": "20px",
            "backgroundColor": "#ffffff",
            "align": "center",
        },
        "htmlTemplate": "",
    },
    # Image blocks
    {
        "type": "ImageBlock01",
        "category": "image",
        "name": "Single image",
        "description": "Full-width image with optional caption",
        "thumbnail": "",
        "defaultContent": {
            "image": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1200",
            "alt": "Image description",
            "caption": "",
        },
        "defaultSettings": {
            "paddingTop": "40px",
            "paddingBottom": "40px",
            "backgroundColor": "#ffffff",
            "align": "center",
        },
        "htmlTemplate": "",
    },
    {
        "type": "GalleryBlock01",
        "category": "image",
        "name": "Image gallery",
        "description": "Grid of images with lightbox",
        "thumbnail": "",
        "defaultContent": {
            "images": [
                {"src": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600", "alt": "Image 1"},
                {"src": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600", "alt": "Image 2"},
                {"src": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=600", "alt": "Image 3"},
                {"src": "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600", "alt": "Image 4"},
            ],
            "columns": 2,
        },
        "defaultSettings": {
            "paddingTop": "40px",
            "paddingBottom": "40px",
            "backgroundColor": "#ffffff",
            "align": "center",
        },
        "htmlTemplate": "",
    },
    # Button block
    {
        "type": "ButtonBlock01",
        "category": "button",
        "name": "Button group",
        "description": "One or two call-to-action buttons",
        "thumbnail": "",
        "defaultContent": {
            "buttons": [
                {"text": "Primary Action", "url": "#", "style": "primary"},
                {"text": "Secondary Action", "url": "#", "style": "outlined"},
            ],
        },
        "defaultSettings": {
            "paddingTop": "40px",
            "paddingBottom": "40px",
            "backgroundColor": "#ffffff",
            "align": "center",
        },
        "htmlTemplate": "",
    },
    # Form blocks
    {
        "type": "FormBlock01",
        "category": "form",
        "name": "Contact form",
        "description": "Simple contact form with name, email, and message fields",
        "thumbnail": "",
        "defaultContent": {
            "title": "Contact Us",
            "subtitle": "Fill out the form and we'll get back to you",
            "fields": [
                {"type": "text", "label": "Name", "placeholder": "Your name", "required": True},
                {"type": "email", "label": "Email", "placeholder": "your@email.com", "required": True},
                {"type": "textarea", "label": "Message", "placeholder": "Your message...", "required": True},
            ],
            "submitText": "Send Message",
            "successMessage": "Thank you! We will contact you soon.",
        },
        "defaultSettings": {
            "paddingTop": "80px",
            "paddingBottom": "80px",
            "backgroundColor": "#f8f9fa",
            "align": "center",
        },
        "htmlTemplate": "",
    },
    {
        "type": "FormBlock02",
        "category": "form",
        "name": "Subscription form",
        "description": "Email subscription form with inline input",
        "thumbnail": "",
        "defaultContent": {
            "title": "Stay Updated",
            "subtitle": "Subscribe to our newsletter",
            "placeholder": "Enter your email",
            "submitText": "Subscribe",
            "successMessage": "You have been subscribed!",
        },
        "defaultSettings": {
            "paddingTop": "60px",
            "paddingBottom": "60px",
            "backgroundColor": "#1a1a2e",
            "align": "center",
        },
        "htmlTemplate": "",
    },
    # Menu blocks
    {
        "type": "MenuBlock01",
        "category": "menu",
        "name": "Navigation bar",
        "description": "Horizontal navigation with logo and links",
        "thumbnail": "",
        "defaultContent": {
            "logo": "My Site",
            "links": [
                {"text": "Home", "url": "#"},
                {"text": "About", "url": "#about"},
                {"text": "Services", "url": "#services"},
                {"text": "Contact", "url": "#contact"},
            ],
            "ctaButton": {"text": "Get Started", "url": "#"},
        },
        "defaultSettings": {
            "paddingTop": "0px",
            "paddingBottom": "0px",
            "backgroundColor": "#ffffff",
            "align": "center",
            "fullWidth": True,
        },
        "htmlTemplate": "",
    },
    {
        "type": "MenuBlock02",
        "category": "menu",
        "name": "Transparent navigation",
        "description": "Transparent overlay navigation bar",
        "thumbnail": "",
        "defaultContent": {
            "logo": "Brand",
            "links": [
                {"text": "Home", "url": "#"},
                {"text": "Portfolio", "url": "#portfolio"},
                {"text": "Blog", "url": "#blog"},
                {"text": "Contact", "url": "#contact"},
            ],
        },
        "defaultSettings": {
            "paddingTop": "0px",
            "paddingBottom": "0px",
            "backgroundColor": "transparent",
            "align": "center",
            "fullWidth": True,
        },
        "htmlTemplate": "",
    },
    # Footer blocks
    {
        "type": "FooterBlock01",
        "category": "footer",
        "name": "Simple footer",
        "description": "Footer with copyright and social links",
        "thumbnail": "",
        "defaultContent": {
            "copyright": "\u00a9 2026 My Company. All rights reserved.",
            "socialLinks": [
                {"icon": "mdi-facebook", "url": "#"},
                {"icon": "mdi-twitter", "url": "#"},
                {"icon": "mdi-instagram", "url": "#"},
            ],
        },
        "defaultSettings": {
            "paddingTop": "40px",
            "paddingBottom": "40px",
            "backgroundColor": "#1a1a2e",
            "align": "center",
        },
        "htmlTemplate": "",
    },
    {
        "type": "FooterBlock02",
        "category": "footer",
        "name": "Multi-column footer",
        "description": "Footer with multiple link columns and contact info",
        "thumbnail": "",
        "defaultContent": {
            "logo": "My Site",
            "description": "Building the future of web design.",
            "columns": [
                {
                    "title": "Company",
                    "links": [
                        {"text": "About", "url": "#"},
                        {"text": "Careers", "url": "#"},
                        {"text": "Blog", "url": "#"},
                    ],
                },
                {
                    "title": "Support",
                    "links": [
                        {"text": "Help Center", "url": "#"},
                        {"text": "Contact", "url": "#"},
                        {"text": "Privacy", "url": "#"},
                    ],
                },
            ],
            "copyright": "\u00a9 2026 My Company",
        },
        "defaultSettings": {
            "paddingTop": "60px",
            "paddingBottom": "40px",
            "backgroundColor": "#0f0f23",
            "align": "left",
        },
        "htmlTemplate": "",
    },
    # Video block
    {
        "type": "VideoBlock01",
        "category": "video",
        "name": "Video embed",
        "description": "Embedded YouTube or Vimeo video",
        "thumbnail": "",
        "defaultContent": {
            "videoUrl": "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "title": "Watch Our Story",
            "aspectRatio": "16/9",
        },
        "defaultSettings": {
            "paddingTop": "60px",
            "paddingBottom": "60px",
            "backgroundColor": "#000000",
            "align": "center",
        },
        "htmlTemplate": "",
    },
    # Divider block
    {
        "type": "DividerBlock01",
        "category": "divider",
        "name": "Horizontal divider",
        "description": "Simple line divider with optional spacing",
        "thumbnail": "",
        "defaultContent": {
            "style": "solid",
            "width": "100px",
            "color": "#dee2e6",
        },
        "defaultSettings": {
            "paddingTop": "30px",
            "paddingBottom": "30px",
            "backgroundColor": "#ffffff",
            "align": "center",
        },
        "htmlTemplate": "",
    },
    # Columns block
    {
        "type": "ColumnsBlock01",
        "category": "columns",
        "name": "Three-column cards",
        "description": "Three cards with icon, title, and description",
        "thumbnail": "",
        "defaultContent": {
            "title": "Our Services",
            "cards": [
                {"icon": "mdi-palette", "title": "Design", "text": "Beautiful, modern designs."},
                {"icon": "mdi-code-braces", "title": "Development", "text": "Robust, scalable solutions."},
                {"icon": "mdi-rocket-launch", "title": "Marketing", "text": "Strategic campaigns."},
            ],
        },
        "defaultSettings": {
            "paddingTop": "80px",
            "paddingBottom": "80px",
            "backgroundColor": "#ffffff",
            "align": "center",
        },
        "htmlTemplate": "",
    },
]
