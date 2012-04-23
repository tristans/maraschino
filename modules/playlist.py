from flask import Flask, render_template
import jsonrpclib
import urllib

from Maraschino import app
from settings import *
from maraschino.noneditable import *
from maraschino.tools import *
import maraschino.logger as logger

global vfs_url
vfs_url = '/xhr/vfs_proxy/'
global xbmc_error
xbmc_error = 'There was a problem connecting to the XBMC server'

@app.route('/xhr/playlist')
@app.route('/xhr/playlist/')
@requires_auth
def xhr_playlist():
	api_address = server_api_address()

	if not api_address:
		logger.log('PLAYLIST :: No XBMC server defined', 'ERROR')
		return render_playlist(message="You need to configure XBMC server settings first.")

	try:
		xbmc = jsonrpclib.Server(api_address)
		current_playlist = []
		title = "Playlist"
		media_type = 0
		
		# determine what we're currently watching.
		# this will tell us what playlist to use
		logger.log('PLAYLIST :: Retrieving active playlist type', 'INFO')

		try:
			active_player = xbmc.Player.GetActivePlayers()
			logger.log('PLAYLIST :: active player: %s' % active_player[0], 'INFO')

			if active_player[0]['type'] == 'video':
				title = "Video Playlist"
				media_type = 1

			if active_player[0]['type'] == 'audio':
				title = "Audio Playlist"
				media_type = 0
			currently_playing = xbmc.Player.GetItem(media_type)['item']
		except:
			currently_playing = {'id': -1}

		logger.log('PLAYLIST :: Currently playing detected as %s ' % currently_playing, 'INFO')

		logger.log('PLAYLIST :: Retrieving playlist info for type %s' % media_type, 'INFO')
		playlist = xbmc.Playlist.GetItems(media_type)
		
		# tweak our items for better output
		item_position = 0
		if playlist.has_key('items'):
			for item in playlist['items']:
				if currently_playing['id'] == item['id']:
					item['currently_playing'] = "True"
				item['position'] = item_position
				item_position += 1
				current_playlist.append(item)

		current_playlist = {'playlist_items': current_playlist}
	except:
		logger.log('PLAYLIST :: %s' % xbmc_error, 'ERROR')
		return render_playlist(message=xbmc_error)

	return render_playlist(current_playlist, title) 

def render_playlist(playlist=None, title="Playlist", message=None):
	return render_template(
		'playlist.html',
		playlist = playlist,
		title = title,
		message = message
	)
