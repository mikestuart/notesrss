Evernote to Static Blog & RSS Service
A service that enables Evernote users to tag notes, which then become content for a static blog and RSS feed. The system consists of three main components:
1. WordPress for User Signup & Evernote OAuth
	- Users sign up via WordPress.
	- The system performs Evernote OAuth authentication to obtain an API access token.
	- No additional UI—everything is fully automated after signup.
2. Python Batch Program 1: Evernote Exporter
	- Uses the Evernote SDK to fetch notes tagged with "publish".
	- Exports each note as HTML with its associated images & attachments.
	- Organizes each user's notes into structured folders.
3. Python Batch Program 2: Pelican Blog Generator
	- Reads the exported Evernote note directories.
	- Generates a static blog using Pelican.
	- Creates an RSS feed for updates.
	- Outputs are hosted on a subdomain for each user.
---

Deployment & Offerings
We are providing two services:

1️⃣ Blog & RSS Hosting (Subdomain Service)
- Each user's blog & RSS feed is hosted on a subdomain (user.notesrss.com).
- Uses Pelican to generate static content.
- Hosted on Plesk/Nginx, S3+CloudFront, or Netlify.

2️⃣ Cloud Storage Export
- Users can export their Evernote notes as HTML, images, and attachments.
- Supports Dropbox, Amazon S3, Azure Blob, and Google Drive.
---

Technical Stack

- Backend: Python, Evernote SDK, Pelican (static site generator)
- Frontend: None (users interact only via Evernote tags)
- Authentication: WordPress (OAuth for Evernote access tokens)
- Storage: Filesystem for batch processing, cloud storage options for exports
- Hosting: Subdomains for blogs, cloud storage for personal archives
- Deployment: Plesk, Nginx, S3+CloudFront, Netlify
---

Current Status
✅ Prototypes for all steps are working
✅ Batch programs successfully process Evernote data
✅ Static blogs & RSS feeds are generated correctly
🚀 Now finalizing production deployment options

Why This Project is Valuable
- Fully automated publishing for Evernote users.
- No learning curve—users just tag notes in Evernote.
- Multiple hosting options—users can have a blog OR export their notes for self-hosting.
