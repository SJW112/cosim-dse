
function [Y]=insert_missing_Yphases(Y)
%missing_phases= [25,28,35,37,38,41,42]';
%missing_phases= [19,22,31,32,35,36,47]';

Y_all_=Y;
% add_zeros=zeros(1,length(Y_all));
% Y_all= [zeros(length(Y_all),1),Y_all];

Y_all_= [Y_all_(:,1:18),zeros(size(Y_all_,1),1),Y_all_(:,19:end)];
Y_all_= [Y_all_(:,1:21),zeros(size(Y_all_,1),1),Y_all_(:,22:end)];
Y_all_= [Y_all_(:,1:30),zeros(size(Y_all_,1),1),Y_all_(:,31:end)];
Y_all_= [Y_all_(:,1:31),zeros(size(Y_all_,1),1),Y_all_(:,32:end)];
Y_all_= [Y_all_(:,1:34),zeros(size(Y_all_,1),1),Y_all_(:,35:end)];
Y_all_= [Y_all_(:,1:35),zeros(size(Y_all_,1),1),Y_all_(:,36:end)];
Y_all_= [Y_all_(:,1:46),zeros(size(Y_all_,1),1),Y_all_(:,47:end)];

Y_all_= [Y_all_(1:18,:);zeros(size(Y_all_,2),1)';Y_all_(19:end,:)];
Y_all_= [Y_all_(1:21,:);zeros(size(Y_all_,2),1)';Y_all_(22:end,:)];
Y_all_= [Y_all_(1:30,:);zeros(size(Y_all_,2),1)';Y_all_(31:end,:)];
Y_all_= [Y_all_(1:31,:);zeros(size(Y_all_,2),1)';Y_all_(32:end,:)];
Y_all_= [Y_all_(1:34,:);zeros(size(Y_all_,2),1)';Y_all_(35:end,:)];
Y_all_= [Y_all_(1:35,:);zeros(size(Y_all_,2),1)';Y_all_(36:end,:)];
Y_all_= [Y_all_(1:46,:);zeros(size(Y_all_,2),1)';Y_all_(47:end,:)];


Y=Y_all_;
end