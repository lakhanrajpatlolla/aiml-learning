package client.akkaPractise

import akka.actor._

/**
  * Created by lpatlolla on 5/7/18.
  */
class Listener extends Actor {
  def receive = {
    case PiApproximation(pi, duration) ⇒
      println("\n\tPi approximation: \t\t%s\n\tCalculation time: \t%s"
        .format(pi, duration))
      context.system.terminate()
  }
}
