---
description: Share a newspaper HTML file instantly via Vercel — returns a live public URL with no auth required
---
Deploy the specified newspaper HTML file to Vercel for public sharing. Run: bash {{skill_dir}}/scripts/share.sh $1

If $1 is omitted, share the most recently modified file in ~/.agent/newspapers/. The script requires the vercel-deploy skill to be installed. Deployments are public (anyone with the URL can view), have a 30-day default retention, and are claimable (transferable to a Vercel account). Report the live URL and claim URL to the user.
