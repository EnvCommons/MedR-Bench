"""Minimal server wrapper for MedRBench environment."""

from openreward.environments import Server

from medrb import MedRBench

if __name__ == "__main__":
    server = Server([MedRBench])
    server.run()
