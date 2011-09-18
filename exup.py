#!/usr/bin/python

# The exup script requires the following python modules:
#  ftputil (python-ftputil)
#  m2crypto (python-m2crypto)
#  m2secret (available at http://www.heikkitoivonen.net/m2secret/)

from subprocess import call
import sys, os, ftputil, shutil, ConfigParser, m2secret, exupconfig

class ExUp:
	
	def run(self):
		
		repo = raw_input('Enter the name of the repository you wish to export & upload: ')
		if not repo:
			print "No repo entered"
			return 1
		
		if not os.path.exists(exupconfig.REPOROOT + repo):
			print "Repo doesn't exist"
			return 1
		
		svnpath = "file://" + exupconfig.REPOROOT + repo
	
		branch = raw_input('Enter the branch (blank for trunk): ')
		if branch:
			svnpath += "/branches/" + branch
		else:
			svnpath += "/trunk"
	
		export = './' + repo
		if os.path.exists(export):
			print "Unable to export to current directory, '" + export + '" already exists'
			return 1
		
		host = False
		try:
			retcode = call(["svn", "export", svnpath, export])
			if (retcode > 0):
				print "SVN export failed."
				return 1
	
			ftpconfigfile = exupconfig.FTPCONFIGFILE
			
			newfile = raw_input('Specify config file (or blank for ' + ftpconfigfile + ')')
			if newfile:
				ftpconfigfile = newfile
			
			config = ConfigParser.RawConfigParser()
			config.readfp(open(ftpconfigfile))
			ftphost = config.get(repo,'host')
			ftpuser = config.get(repo,'user')
	
			secretkey = raw_input('Enter your encryption key for the FTP password (or blank for unencrypted): ')
			if secretkey:
				secret = m2secret.Secret()
				secret.deserialize(config.get(repo,'pass'))
				ftppass = secret.decrypt(secretkey)
			else:
				ftppass = config.get(repo,'pass')
			
			try:
				print "Logging into:", ftphost, "with login:", ftpuser, "..."
				host = ftputil.FTPHost(ftphost, ftpuser, ftppass)
			except AttributeError:
				print "FTP connection failed: please check ftp host and login and try again..."
				return 1
			except ftputil.ftp_error.FTPError, err:
				print "FTP connection failed: please check ftp host, login and password and try again..."
				print err
				return 1
			
			exportl = len(export)
			spath = config.get(repo,'path')
			for root, dirs, files in os.walk(export):
		
				prefix = root[exportl:]
				if (len(prefix) > 0):
					prefix = prefix[1:] + '/'
			
				for d in dirs:
					if not host.path.isdir(spath + d):
						host.makedirs(spath + d)
						print "created directory", spath + d
	
				for f in files:
					if host.upload_if_newer(export + '/' + prefix + f, spath + prefix + f):
						print "uploaded", spath + prefix + f
		finally:
			if host:
				host.close()	
	
			if os.path.exists(export):
				shutil.rmtree(export)
		
		return 0

if __name__ == '__main__':
	exup = ExUp()
	sys.exit(exup.run())
