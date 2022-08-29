from time import sleep

class A():
   def b(self):
      print("adam")
      self.a()
      print("koniec")
   def a(self):
      sleep(0)
      print("1")
      print("2")
      sleep(2)
      print("3")
      sleep(2)
      print("4")
B=A()
B.b()