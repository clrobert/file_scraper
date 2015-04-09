import sys
import os
import re
import urllib2
import urllib
import time
from sets import Set
from BeautifulSoup import BeautifulSoup

def main():
  global site
  global format
  global base_path

  base_path = "downloads/"

  if not os.path.exists(base_path):
    os.makedirs(base_path)

  if not "http" in sys.argv[1]:
    site = "http://" + sys.argv[1]
  else:
    site = sys.argv[1]

  format = sys.argv[2]
  print format

  try:
    runScraper(format)
  except urllib2.HTTPError:
    print "Are you sure you're online?"

# Grab the given url's html and make it pretty. Returns an object of type BeautifulSoup
def getPage(url):
  if isRelativePath(url):
    url = site + url
  return BeautifulSoup(urllib2.urlopen(url).read())

def isRelativePath(path):
  out_link = re.compile("http")
  return not out_link.match(path)

# Pops a link off the list of links, returning only the first relative link
def chooseLink(links, regex):
  return links.pop()

# Return all followable links.
# @NOTE: NYI
def removeExternalUrls(links):
  urls = []

  for link in links:
    if isRelativePath(link):
      urls.append(link)

  return urls

def removeJavascript(urls):
  return pruneListByRegex(urls, "javascript")

# Return all downloadable links which match our preferences.
# Preferences NYI
def getDownloadLinks(urls, file_format):
  return getUrlsByRegex(urls, file_format)

def removeRelativeLocationUrls(urls):
  return pruneListByRegex(urls, "comment")

def pruneListByRegex(a_list, format):
  results = []
  format = re.compile(format)
  for item in a_list:
    print item
    candidate = parseFilename(item)
    if candidate is not '' and not format.match(candidate):
      results.append(item)
  return results

def getUrlsByRegex(urls, format):
#  print format

  results = []
  format = re.compile(format); #print urls
  for url in urls:
    candidate = parseFilename(url)
    if format.findall(candidate):
      results.append(url)
  return results

# Return urls given anchor hyperlink reference tags.
def parseLinks(link_list):
  urls = []
  for html_link in link_list:
    urls.append(parseLink(html_link))
  return urls

# Individual helper method.
def parseLink(tag_link):
  if tag_link.has_key("href"):
    tag_link = tag_link['href']
    url = tag_link.encode('ascii')
  else:
    url = ''
  return url

# Remove all links which have already been downloaded.
# @NOTE: NYI
def removeDownloaded(links):
  return links

# Remove all links which have already been downloaded.
# @NOTE: NYI
def removeFollowed(urls, followed):  

  s_urls = Set(urls)
  s_followed = Set(followed)

  s_urls.difference_update(s_followed)

  return s_urls

# Download all of the files from the given links.
# @NOTE: NYI
def downloadFiles(fileNames, fileLinks):
  if len(fileNames) > 1 :
    for name,link in fileNames,fileLinks:
      names = downloadFile(name, link)
  else:
    downloadFile(fileNames.pop(), fileLinks.pop())

# Open a "web file" and write it to the current directory.
# @TODO: autopopulate a directory structure and give options.
def downloadFile(write_to, read_from):
  file = open(base_path + write_to, 'w')
  print >> file, (site + read_from)

# Return filenames given urls.
def parseFilenames(links):
  names = []
  for link in links:
    names.append(parseFilename(link))
  return names

# Individual helper method.
def parseFilename(link):
  filename = re.split("/", link).pop()
  if filename is None:
    filename = ''
  return filename

def runScraper(file_format):
  follow_links = []
  print "Scraping " + site + " ..."
  url = site;
  follow_links.append(site)
  followed = []

  while (follow_links):
    try:
      #time.sleep(1)
      # Grab the next link to follow 
      url = chooseLink(follow_links, "http"); print url

      # Add url to followed before traversed: in case of exception.
      followed.append(url); #print followed

      # Grab the next page
      cur_page = getPage(url); #print cur_page("a")

      # Get a list of the links from the current page and add them to be traversed
      all_page_links = cur_page("a");# print "Links from page grabbed."; #print all_page_links

      all_page_urls = parseLinks(all_page_links); #print "Hyperlink anchors removed from potential links.";# print all_page_urls

      all_page_urls = removeJavascript(all_page_urls)

      all_page_urls = removeRelativeLocationUrls(all_page_urls)



      internal_urls = removeExternalUrls(all_page_urls);# print "Purged external urls from potential links."; #print follow_links

      follow_links.extend(removeFollowed(internal_urls, followed) );# print "Followed links removed from potential links. Potential links saved.";

      # Check the current page for candidate download links. Use all_page_urls, because media hosting may be under
      # a subdomain, or externally hosted.
      download_links = getDownloadLinks(all_page_urls, file_format); print "Parsed candidate download links:"

      if download_links:
        filenames = parseFilenames(download_links); print "File names parsed."

        # Remove all already downloaded files from the list 
        # Print each collision to stdout
        download_links = removeDownloaded(download_links); print "Download collisions purged."  

        # Download all candidate links
        downloadFiles(filenames, download_links); print "Files on current page downloaded."
      else:
        print "No suitable downloads found on this page."
        print download_links

    except urllib2.HTTPError:
      print "Could not follow link."

    

  ## Recurse
  print "All paths have been traversed."

main()
