

function [Vmag,Vph]=Three_phase(IEEE13)

% structs where the results of the state estimates are stored
results_DSSE_WLS2=struct;
results_DSSE_WLS2.err_Vmagnitude=[];
results_DSSE_WLS2.err_Vphase=[];
results_DSSE_WLS2.Vmagn_status=[];
results_DSSE_WLS2.Vph_status=[];
results_DSSE_WLS2.Imagn_status=[];
results_DSSE_WLS2.Iph_status=[];
results_DSSE_WLS2.Vreal_status=[];
results_DSSE_WLS2.Vimag_status=[];
results_DSSE_WLS2.Ireal_status=[];
results_DSSE_WLS2.Iimag_status=[];
results_DSSE_WLS2.Vmagn_true=[];
results_DSSE_WLS2.Vph_true=[];
results_DSSE_WLS2.Imagn_true=[];
results_DSSE_WLS2.Iph_true=[];
results_DSSE_WLS2.Vreal_true=[];
results_DSSE_WLS2.Vimag_true=[];
results_DSSE_WLS2.Ireal_true=[];
results_DSSE_WLS2.Iimag_true=[];
results_DSSE_WLS2.err_Imagnitude=[];
results_DSSE_WLS2.err_Iphase=[];
results_DSSE_WLS2.err_Ireal=[];
results_DSSE_WLS2.err_Iimag=[];
results_DSSE_WLS2.err_Vreal=[];
results_DSSE_WLS2.err_Vimag=[];
results_DSSE_WLS2.err_Vmagnitude_in=[];
results_DSSE_WLS2.err_Vphase_in=[];
results_DSSE_WLS2.err_Imagnitude_in  =[];
results_DSSE_WLS2.err_Iphase_in   =[];
results_DSSE_WLS2.err_Ireal_in   =[];
results_DSSE_WLS2.err_Iimag_in =[];
results_DSSE_WLS2.Vmagn_measured =[];
results_DSSE_WLS2.Vph_measured =[];
results_DSSE_WLS=struct;
results_DSSE_WLS.err_Vmagnitude=[];
results_DSSE_WLS.err_Vphase=[];
results_DSSE_WLS.Vmagn_status=[];
results_DSSE_WLS.Vph_status=[];
results_DSSE_WLS.Imagn_status=[];
results_DSSE_WLS.Iph_status=[];
results_DSSE_WLS.Vreal_status=[];
results_DSSE_WLS.Vimag_status=[];
results_DSSE_WLS.Ireal_status=[];
results_DSSE_WLS.Iimag_status=[];
results_DSSE_WLS.Vmagn_true=[];
results_DSSE_WLS.Vph_true=[];
results_DSSE_WLS.Imagn_true=[];
results_DSSE_WLS.Iph_true=[];
results_DSSE_WLS.Vreal_true=[];
results_DSSE_WLS.Vimag_true=[];
results_DSSE_WLS.Ireal_true=[];
results_DSSE_WLS.Iimag_true=[];
results_DSSE_WLS.err_Imagnitude=[];
results_DSSE_WLS.err_Iphase=[];
results_DSSE_WLS.err_Ireal=[];
results_DSSE_WLS.err_Iimag=[];
results_DSSE_WLS.err_Vreal=[];
results_DSSE_WLS.err_Vimag=[];
results_DSSE_WLS.err_Vmagnitude_in   =[];
results_DSSE_WLS.err_Vphase_in=[];
results_DSSE_WLS.err_Imagnitude_in  =[];
results_DSSE_WLS.err_Iphase_in   =[];
results_DSSE_WLS.err_Ireal_in   =[];
results_DSSE_WLS.err_Iimag_in =[];
results_DSSE_WLS.Vmagn_measured =[];
results_DSSE_WLS.Vph_measured =[];


[GridData] =Griddata(IEEE13);%in this function the static model is generated
[PowerData]=PowerDData(GridData,IEEE13);
[Test_SetUp,Combination_devices,Accuracy]=DSSEConfData(GridData);%here the test configuration data are set: measurement devices location and accuracy
GridData.rm_column = 0;%in this case the phase angle at 1st bus is also considered as state
[W,GridData,R] = Weightm(GridData,PowerData,Combination_devices,Accuracy); %weight and covariance matrix of the state estimator
[Meas_true_vector] = calc_Mvector_external(GridData,PowerData); %vector with reference values of the measurements

PowerData.Pinj
PowerData.Qinj
%% State Estimation
Test_SetUp.N_MC=10;
warning off
for z = 1 : Test_SetUp.N_MC %in this for loop the Monte Carlo tests are run
    Meas_vector_external = mvnrnd(Meas_true_vector, R)'; %the measurements are corrupted following the covariance matrix
%     [Vmagn_status_WLS,Vph_status_WLS]   =  IRIDSSE(PowerData,W,GridData,Test_SetUp); %voltage state estimator
    % [Vmagn_status_WLS,Vph_status_WLS]   =  VRIDSSE(Meas_vector_external,W,GridData,Test_SetUp); %voltage state estimator
    [Vmagn_status_WLS,Vph_status_WLS]   =  VRIDSSE(PowerData,W,GridData,Test_SetUp);
%     [results_DSSE_WLS]              = DataOutput(Vmagn_status_WLS,Vph_status_WLS,results_DSSE_WLS,GridData,PowerData); %collects the metrics of the error
end
% [results_DSSE_Uncertainty_WLS]  = calcUncDSSE(results_DSSE_WLS,GridData,Test_SetUp); %calculate uncertainty of the estimator

Vmag=reshape(Vmagn_status_WLS,1,[]);
Vph=reshape(Vph_status_WLS,1,[]);

Vmagtrue=PowerData.Vmagn;
Vphtrue=PowerData.Vph;
end