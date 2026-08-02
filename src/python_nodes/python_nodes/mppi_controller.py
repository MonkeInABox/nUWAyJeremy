import numpy as np

class MPPIController:
    def __init__(self, num_samples=10, horizon=5, lambda_=1.0, dt=0.02):
        self.num_samples = num_samples  # Number of sampled control sequences
        self.horizon = horizon  # Planning horizon
        self.lambda_ = lambda_  # Temperature parameter for softmin
        self.dt = dt  # Time step
        self.u_nominal = np.zeros(horizon)  # Initial nominal control sequence

    def vehicle_dynamics(self, v, a):
        """ Computes next velocity given current velocity and acceleration """
        return v + a * self.dt
    
    def compute_cost(self, v_traj, selected_speed):
        cost = np.sum((v_traj - selected_speed) ** 2)  # Penalize deviation from target velocity
        return cost

    def optimize(self, speed_fb, selected_speed):
        """ Runs MPPI optimization to find the best acceleration command """
        # Sample control sequences from a Gaussian distribution
        sampled_accels = np.random.normal(loc=self.u_nominal, scale=1.0, size=(self.num_samples, self.horizon))
        sampled_accels = np.clip(sampled_accels, -1.5, 1.5)  # Limit acceleration between -1 and 1 m/s
        costs = np.zeros(self.num_samples)
        
        # Evaluate sampled trajectories
        for i in range(self.num_samples):
            v = speed_fb
            v_traj = []
            for t in range(self.horizon):
                v = self.vehicle_dynamics(v, sampled_accels[i, t])
                v_traj.append(v)
            costs[i] = self.compute_cost(np.array(v_traj), selected_speed)
        
        # Compute softmin weights
        beta = np.min(costs)
        weights = np.exp(- (costs - beta) / self.lambda_)
        weights /= np.sum(weights)
        
        # Compute the optimal control by taking the weighted sum
        optimal_control = np.sum(weights[:, None] * sampled_accels, axis=0)
        
        # Update the nominal control sequence
        self.u_nominal = np.roll(self.u_nominal, -1)
        self.u_nominal[-1] = optimal_control[0]
        
        return optimal_control[0]  # Return first control action