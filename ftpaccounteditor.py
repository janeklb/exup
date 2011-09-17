#!/usr/bin/python

import sys, ConfigParser, m2secret, traceback

FTPOPTIONS = { 'host': False, 'user': False, 'pass': True, 'path': False }

# Edit an FTP config section
def edit_ftp():
	global hasedits

	section = raw_input('Enter section to edit: ')
	option = raw_input('Enter option to edit: ')
	value = raw_input('Enter value for ' + option + ': ')

	if option in FTPOPTIONS and FTPOPTIONS[option] == True:
		print 'serializing'
		secret.encrypt(value, secretkey)
		value = secret.serialize()
	
	config.set(section, option, value)
	hasedits = True
	
# Add an FTP config section
def add_ftp():
	global hasedits
	
	section = raw_input('Enter section name: ')
	config.add_section(section)
	hasedits = True

	for option, encrypt in FTPOPTIONS.iteritems():
		value = ''
		if (encrypt):
			secret.encrypt(raw_input('Enter ' + option + ': '), secretkey)
			value = secret.serialize()
		else:
			value = raw_input('Enter ' + option + ': ')
		print 'Setting', option, 'to', value
		config.set(section, option, value)

# Display FTP
def display_ftp():
	options = config.items(raw_input('Enter section name: '))
	print options

def main():
	hasedits 	= False
	configfile 	= exupconfig.FTPCONFIGFILE
	configfilefp 	= open(configfile)

	config 		= ConfigParser.RawConfigParser(allow_no_value=True)
	config.readfp(configfilefp)

	secret 		= m2secret.Secret()
	secretkey 	= raw_input('Enter your encryption key for the FTP password: ')
	print 'Loaded sections:', config.sections()

	while (True):
		try:
			command = raw_input('Add (a), Edit (e), Display (d), Quit (q): ')
			if command == 'a':
				add_ftp()
			elif command == 'e':
				edit_ftp()
			elif command == 'd':
				display_ftp()
			elif command == 'q':

				if hasedits:

					save = raw_input('Would you like to save changes to ' + configfile + '? [Y/n]')

					if save == 'Y' or save == 'y':
						configfilefp.close()
						with open(configfile, 'wb') as configfilefp:
							config.write(configfilefp)
							print configfile, 'saved'
					
				configfilefp.close()
				print 'Bye!'
				return 0
			else:
				print 'Unknown command'

		except Exception:
			traceback.print_exc()
	
	return 0

if __name__ == '__main__':
    sys.exit(main())
