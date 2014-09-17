#!/usr/bin/env python2
import os
import sys
import thread
import time
sys.path.insert(0, '/usr/lib/Leap')
import Leap as L
from Leap import CircleGesture

def call_amixer():
	pass

def set_volume():
	pass

print "Leap imported."

class SampleListener(L.Listener):
	finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
	bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
	state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
	pvol = 0
	volume = 0
	muted = False

	def set_volume(self, volume):
		vol = min(64, max(0, int(volume)))
		if vol != self.pvol:
			self.pvol = vol
			os.system('amixer -q sset Master %d' % vol)
			print 'Set volume to %d' % vol

	def save_volume(self):
		self.volume = self.pvol
		print 'Saved volume to %d' % self.pvol

	def mute(self):
		self.muted = True
		os.system('amixer -q sset Master toggle')
		print 'Muted volume'

	def unmute(self):
		self.muted = False
		os.system('amixer -q sset Master toggle')
		print 'Unmuted volume'

	def on_init(self, controller):
		print "Initialized"

	def on_connect(self, controller):
		print "Connected"

		# Enable gestures
		controller.enable_gesture(L.Gesture.TYPE_CIRCLE);
		controller.enable_gesture(L.Gesture.TYPE_KEY_TAP);
		controller.enable_gesture(L.Gesture.TYPE_SCREEN_TAP);
		controller.enable_gesture(L.Gesture.TYPE_SWIPE);

	def on_disconnect(self, controller):
		# Note: not dispatched when running in a debugger.
		print "Disconnected"

	def on_exit(self, controller):
		print "Exited"

	def on_frame(self, controller):
		# Get the most recent frame and report some basic information
		frame = controller.frame()

		# Check for mute
		if self.muted and len(frame.hands) == 0:
			self.unmute()

		for hand in frame.hands:
			if self.muted and len(hand.fingers.extended()) < 5:
				self.unmute()
				break
			if not self.muted and len(hand.fingers.extended()) == 5:
				self.mute()
				break

		# Get gestures
		for gesture in frame.gestures():
			if gesture.type == L.Gesture.TYPE_CIRCLE:
				circle = CircleGesture(gesture)

				# Determine clock direction using the angle between the pointable and the circle normal
				if circle.pointable.direction.angle_to(circle.normal) <= L.PI/2:
					clockwiseness = "clockwise"
				else:
					clockwiseness = "counterclockwise"

				# Calculate the angle swept since the last frame
				swept_angle = 0
				if circle.state != L.Gesture.STATE_START:
					previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
					swept_angle =  (circle.progress - previous_update.progress) * 2 * L.PI

				mod = circle.progress * 3
				if clockwiseness == 'counterclockwise':
					mod = -mod

				self.set_volume(self.volume + mod)

				if gesture.state == 3:
					self.save_volume()

def main():
	# Create a sample listener and controller
	listener = SampleListener()
	controller = L.Controller()

	# Have the sample listener receive events from the controller
	controller.add_listener(listener)

	# Keep this process running until Enter is pressed
	print "Press Enter to quit..."
	try:
		sys.stdin.readline()
	except KeyboardInterrupt:
		pass
	finally:
		# Remove the sample listener when done
		controller.remove_listener(listener)

main()
