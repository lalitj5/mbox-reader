last year we had to back up our school emails because it was going to be deleted once we graduate

when i did this, i downloaded my email inbox as an mbox file format, something unfamiliar, so i made this program to be able to parse through the emails so i could access them easier

websites i found online to do this have too many advertisements plastered all over the page, rendering the service worthless, so feel free to use this in your terminal

to start the program, drag your mbox file into the repository. Change the

MBOX_PATH = os.path.join(os.path.dirname(__file__), 'dataset.mbox')

to the filename of your choice, which corresponds to what your mbox file is named.

then run it by using **python inbox.py**

Commands:  [number] open email  |  s  search  |  n  next page  |  p  prev page  |  r  reset  |  q  quit (or ctrl + c)
