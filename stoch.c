#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

void free_all(double* ptrx){
    free(ptrx);
}

double dWT()
{
    int num = 30;
    double dw = (rand() % (2*num + 1)) - num;
    return dw / 10.0;
}

double* SimulatePortfolio(double* S, double* W, double* Drift, double* Volt, int n, int portfolios, double t)
{
    srand(time(NULL));

    for(int i = 0; i < n; ++i){
        printf("%f %f %f %f\n", S[i], W[i], Drift[i], Volt[i]);
    }
    
    int steps = 1000;
    double dt = t / (double) steps;
    double* ror = malloc(n*sizeof(double));
    double* final_boss = malloc(portfolios*sizeof(double));

    for(int p = 0; p < portfolios; ++p){
        final_boss[p] = 0.0;
        for(int k = 0; k < n; ++k){
            double S0 = S[k];
            for(int t = 0; t < steps; ++t){
                S0 += Drift[k]*S0*dt + Volt[k]*S0*dWT();
            }
            ror[k] = W[k]*(S0 / S[k] - 1.0);
        }
        for(int k = 0; k < n; ++k){
            final_boss[p] += ror[k];
        }
        
    }

    free(ror);

    return final_boss;
}

