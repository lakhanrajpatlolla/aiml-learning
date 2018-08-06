import tensorflow as tf
import numpy as np

print(tf.__version__)

a = np.array([5, 3, 8])
b = np.array([3, -1, 2])
c = np.add(a, b)
print(c)

a = tf.constant([5, 3, 8])
b = tf.constant([3, -1, 2])
c = tf.add(a, b)
print(c)


with tf.Session() as sess:
  result = sess.run(c)
  print(result)
  
  
  a = tf.placeholder(dtype=tf.int32, shape=(None,))  # batchsize x scalar
b = tf.placeholder(dtype=tf.int32, shape=(None,))
c = tf.add(a, b)
with tf.Session() as sess:
  result = sess.run(c, feed_dict={
      a: [3, 4, 5],
      b: [-1, 2, 3]
    })
  print(result)
  
  
  
a = tf.placeholder(dtype=tf.int32, shape=(None,))  # batchsize x scalar
b = tf.placeholder(dtype=tf.int32, shape=(None,))
c = tf.add(a, b)
with tf.Session() as sess:
  result = sess.run(c, feed_dict={
      a: [3, 4, 5],
      b: [-1, 2, 3]
    })
  print(result)
  
  
  
  with tf.Session() as sess:
  sides = tf.placeholder(tf.float32, shape=(None, 3))  # batchsize number of triangles, 3 sides
  area = compute_area(sides)
  result = sess.run(area, feed_dict = {
      sides: [
        [5.0, 3.0, 7.1],
        [2.3, 4.1, 4.8]
      ]
    })
  print(result)
  
  
  
  
  import tensorflow as tf

tf.enable_eager_execution()

def compute_area(sides):
  # slice the input to get the sides
  a = sides[:,0]  # 5.0, 2.3
  b = sides[:,1]  # 3.0, 4.1
  c = sides[:,2]  # 7.1, 4.8
  
  # Heron's formula
  s = (a + b + c) * 0.5   # (a + b) is a short-cut to tf.add(a, b)
  areasq = s * (s - a) * (s - b) * (s - c) # (a * b) is a short-cut to tf.multiply(a, b), not tf.matmul(a, b)
  return tf.sqrt(areasq)

area = compute_area(tf.constant([
      [5.0, 3.0, 7.1],
      [2.3, 4.1, 4.8]
    ]))


print(area)



import tensorflow as tf
print(tf.__version__)

def some_method(data):
  a = data[:,0:2]
  c = data[:,1]
  s = (a + c)
  return tf.sqrt(tf.matmul(s, tf.transpose(s)))

with tf.Session() as sess:
  fake_data = tf.constant([
      [5.0, 3.0, 7.1],
      [2.3, 4.1, 4.8],
      [2.8, 4.2, 5.6],
      [2.9, 8.3, 7.3]
    ])
  print sess.run(some_method(fake_data))
  
  
  def some_method(data):
  a = data[:,0:2]
  print a.get_shape()
  c = data[:,1]
  print c.get_shape()
  s = (a + c)
  return tf.sqrt(tf.matmul(s, tf.transpose(s)))

with tf.Session() as sess:
  fake_data = tf.constant([
      [5.0, 3.0, 7.1],
      [2.3, 4.1, 4.8],
      [2.8, 4.2, 5.6],
      [2.9, 8.3, 7.3]
    ])
  print sess.run(some_method(fake_data))
  
  
  def some_method(data):
  a = data[:,0:2]
  print a.get_shape()
  c = data[:,1:3]
  print c.get_shape()
  s = (a + c)
  return tf.sqrt(tf.matmul(s, tf.transpose(s)))

with tf.Session() as sess:
  fake_data = tf.constant([
      [5.0, 3.0, 7.1],
      [2.3, 4.1, 4.8],
      [2.8, 4.2, 5.6],
      [2.9, 8.3, 7.3]
    ])
  print sess.run(some_method(fake_data))
  
  
  import tensorflow as tf

x = tf.constant([[3, 2],
                 [4, 5],
                 [6, 7]])
print "x.shape", x.shape
expanded = tf.expand_dims(x, 1)
print "expanded.shape", expanded.shape
sliced = tf.slice(x, [0, 1], [2, 1])
print "sliced.shape", sliced.shape

with tf.Session() as sess:
  print "expanded: ", expanded.eval()
  print "sliced: ", sliced.eval()
  
  
  def some_method(data):
  print data.get_shape()
  a = data[:,0:2]
  print a.get_shape()
  c = data[:,1:3]
  print c.get_shape()
  s = (a + c)
  return tf.sqrt(tf.matmul(s, tf.transpose(s)))

with tf.Session() as sess:
  fake_data = tf.constant([5.0, 3.0, 7.1])
  print sess.run(some_method(fake_data))
  
  
  def some_method(data):
  print data.get_shape()
  a = data[:,0:2]
  print a.get_shape()
  c = data[:,1:3]
  print c.get_shape()
  s = (a + c)
  return tf.sqrt(tf.matmul(s, tf.transpose(s)))

with tf.Session() as sess:
  fake_data = tf.constant([5.0, 3.0, 7.1])
  fake_data = tf.expand_dims(fake_data, 0)
  print sess.run(some_method(fake_data))
  
  
  def some_method(a, b):
  s = (a + b)
  return tf.sqrt(tf.matmul(s, tf.transpose(s)))

with tf.Session() as sess:
  fake_a = tf.constant([
      [5.0, 3.0, 7.1],
      [2.3, 4.1, 4.8],
    ])
  fake_b = tf.constant([
      [2, 4, 5],
      [2, 8, 7]
    ])
  print sess.run(some_method(fake_a, fake_b))
  
  
def some_method(a, b):
  b = tf.cast(b, tf.float32)
  s = (a + b)
  return tf.sqrt(tf.matmul(s, tf.transpose(s)))

with tf.Session() as sess:
  fake_a = tf.constant([
      [5.0, 3.0, 7.1],
      [2.3, 4.1, 4.8],
    ])
  fake_b = tf.constant([
      [2, 4, 5],
      [2, 8, 7]
    ])
  print sess.run(some_method(fake_a, fake_b))
  
  
  
  import tensorflow as tf
from tensorflow.python import debug as tf_debug

def some_method(a, b):
  b = tf.cast(b, tf.float32)
  s = (a / b)
  s2 = tf.matmul(s, tf.transpose(s))
  return tf.sqrt(s2)

with tf.Session() as sess:
  fake_a = [
      [5.0, 3.0, 7.1],
      [2.3, 4.1, 4.8],
    ]
  fake_b = [
      [2, 0, 5],
      [2, 8, 7]
    ]
  a = tf.placeholder(tf.float32, shape=[2, 3])
  b = tf.placeholder(tf.int32, shape=[2, 3])
  k = some_method(a, b)
  
  # Note: won't work without the ui_type="readline" argument because
  # Datalab is not an interactive terminal and doesn't support the default "curses" ui_type.
  # If you are running this a standalone program, omit the ui_type parameter and add --debug
  # when invoking the TensorFlow program
  #      --debug (e.g: python debugger.py --debug )
  sess = tf_debug.LocalCLIDebugWrapperSession(sess, ui_type="readline")
  sess.add_tensor_filter("has_inf_or_nan", tf_debug.has_inf_or_nan)
  print sess.run(k, feed_dict = {a: fake_a, b: fake_b})
  
  
  
  %writefile debugger.py
import tensorflow as tf

def some_method(a, b):
  b = tf.cast(b, tf.float32)
  s = (a / b)
  print_ab = tf.Print(s, [a, b])
  s = tf.where(tf.is_nan(s), print_ab, s)
  return tf.sqrt(tf.matmul(s, tf.transpose(s)))

with tf.Session() as sess:
  fake_a = tf.constant([
      [5.0, 3.0, 7.1],
      [2.3, 4.1, 4.8],
    ])
  fake_b = tf.constant([
      [2, 0, 5],
      [2, 8, 7]
    ])
  
  print sess.run(some_method(fake_a, fake_b))