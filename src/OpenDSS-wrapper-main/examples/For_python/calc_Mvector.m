%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Function to generate the measurement vector from PowerData structure
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [Meas_vector] = calc_Mvector(GridData,PowerData)
Meas_vector=zeros(GridData.MeasNum,1);
inj_status = 0;
    for n = 1 : GridData.MeasNum

        if GridData.TypeMeas(n,1)==1 %active power
            Meas_vector(n,1)= PowerData.Pinj(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1));
        end
        if GridData.TypeMeas(n,1)==2 %reactive power
            Meas_vector(n,1)= PowerData.Qinj(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1));
        end
        if GridData.TypeMeas(n,1)==3 %voltage magnitude - translated to Vreal
                Meas_vector(n,1)=+real(PowerData.Vmagn(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1))*exp(sqrt(-1)*PowerData.Vph(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1))));
        end
        if GridData.TypeMeas(n,1)==4 %voltage phase angle - translated to Vimag
                Meas_vector(n,1)=+imag(PowerData.Vmagn(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1))*exp(sqrt(-1)*PowerData.Vph(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1))));
        end
        if GridData.TypeMeas(n,1)==5 %current magnitude - translated to Ireal
                Meas_vector(n,1)=+real((PowerData.Imagn(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1)))*exp(sqrt(-1)*PowerData.Iph(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1))));
        end
        if GridData.TypeMeas(n,1)==6 %current phase - translated to Iimag
                Meas_vector(n,1)=+imag((PowerData.Imagn(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1)))*exp(sqrt(-1)*PowerData.Iph(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1))));
        end
        if GridData.TypeMeas(n,1)==7 %pflow  - translated to Ireal
                Meas_vector(n,1)=PowerData.Pflow(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1));
        end
        if GridData.TypeMeas(n,1)==8 %qflow -  - translated to Ireal
                Meas_vector(n,1)=PowerData.Qflow(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1));
        end
    end
end

