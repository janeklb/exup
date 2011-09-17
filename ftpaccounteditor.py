#!/usr/bin/python

import sys, ConfigParser, m2secret, traceback, exupconfig, ftplib, ftputil

class FTPAccountEditor:

	def __init__(self):
		self.FTPOPTIONS 	= { 'host': False, 'user': False, 'pass': True, 'path': False }
		self.hasedits 		= False

		self.configfile 	= exupconfig.FTPCONFIGFILE
		self.configfilefp 	= open(self.configfile)

		self.config 		= ConfigParser.RawConfigParser(allow_no_value=True)
		self.config.readfp(self.configfilefp)
		
		print 'Loaded repositories:', self.config.sections()
	
	def is_option(self, option):
		return option in self.FTPOPTIONS
		
	# Edit an FTP config section
	def edit_ftp(self):

		repo = raw_input('Enter repository to edit: ')
		if not self.config.has_section(repo):
			print "This repository doesn't have any FTP info"
			return
		
		option = raw_input('Enter option to edit: ')
		if not self.is_option(option):
			print "That's not a valid FTP option"
			return
		
		value = raw_input('Enter value for ' + option + ': ')

		if self.is_option(option) and self.FTPOPTIONS[option] == True and self.secretkey:
			self.secret.encrypt(value, self.secretkey)
			value = self.secret.serialize()
	
		self.config.set(repo, option, value)
		self.hasedits = True
	
	# Add an FTP config section
	def add_ftp(self):
	
		repo = raw_input('Enter repository name: ')
		options = {}
		rawpass = ''

		for option, encrypt in self.FTPOPTIONS.iteritems():
			value = raw_input('Enter ' + option + ': ')
			if not value:
				print "Empty options are invalid, please try again"
				return
			
			if option == 'pass':
				rawpass = value

			if option == 'path' and value[0] != '/':
				value = '/' + value

			if (encrypt and self.secretkey):
				self.secret.encrypt(value, self.secretkey)
				value = self.secret.serialize()

			options[option] = value
		
		try:
			print "Attempting connection: " + options['user'] + ":" + rawpass + "@" + options['host'] + options['path']
			host = ftputil.FTPHost(options['host'], options['user'], rawpass)
			if not host.path.isdir(options['path']):
				raise Exception("Specified path is not a directory")
		except Exception, err:
			print err
			print "Unable to connect using specified parameters -- options for " + repo + " will not be saved. Please try again."
		else:
			self.config.add_section(repo)
			for option, value in options:
				self.config.set(repo, option, value)
			self.hasedits = True
			print "Added settings for " + repo + ". Changes won't be saved until exit."

	# Display FTP
	def display_ftp(self):
		section = raw_input('Display repository: ')
		if not self.config.has_section(section):
			print "This repository doesn't have any FTP info"
			return
			
		for o in self.config.items():
			option = o[0]
			value = o[1]
			if self.is_option(option) and self.FTPOPTIONS[option] == True and self.secretkey:
				self.secret.deserialize(value)
				value = self.secret.decrypt(self.secretkey) + " (decrypted)"
			print option + ": " + value
	
	def run(self):

		self.secret 	= m2secret.Secret()
		self.secretkey 	= raw_input('Enter your encryption key for the FTP password (or blank for no encryption): ')

		while (True):
			try:
				command = raw_input('Add (a), Edit (e), Display (d), Quit (q): ')
				if command == 'a':
					self.add_ftp()
				elif command == 'e':
					self.edit_ftp()
				elif command == 'd':
					self.display_ftp()
				elif command == 'q':

					if self.hasedits:
						if raw_input('Would you like to save changes to ' + configfile + '? [Y/N]').lowercase() == 'y':
							self.configfilefp.close()

							with open(self.configfile, 'wb') as self.configfilefp:
								self.config.write(self.configfilefp)
								print self.configfile, 'saved'
					
					self.configfilefp.close()
					print 'Bye!'
					return 0
				else:
					print 'Unknown command'
			except Exception:
				traceback.print_exc()
	
		return 0


if __name__ == '__main__':
	ftpae = FTPAccountEditor()
	sys.exit(ftpae.run())
